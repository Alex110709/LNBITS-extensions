"""
Background tasks for automatic fee adjustment.

This module should be called periodically (e.g., via cron job or task scheduler)
to automatically adjust channel fees based on configured policies.
"""

import asyncio
import time
from typing import List, Dict, Any
import logging

from .crud import (
    get_enabled_policies,
    create_adjustment,
)
from .models import (
    FeePolicy,
    ChannelInfo,
    CreateFeeAdjustment,
)
from .utils import (
    calculate_liquidity_ratio,
    calculate_optimal_fees,
    should_adjust_fees,
    clamp_fee_adjustment,
    get_adjustment_reason,
)

logger = logging.getLogger(__name__)


async def get_channels_from_wallet(wallet_id: str) -> List[ChannelInfo]:
    """
    Fetch channel information from the Lightning node.

    NOTE: This is a placeholder implementation.
    In production, this should use the actual LND/CLN API to get channel data.
    """
    # TODO: Implement actual channel fetching from Lightning node
    # This would typically use:
    # - LND: listchannels RPC call
    # - CLN: listpeers or listchannels command
    # - Or LNbits funding source API

    # For now, return empty list
    # In production, replace with actual implementation
    return []


async def update_channel_fees(
    wallet_id: str,
    channel_id: str,
    base_fee: int,
    fee_rate: int,
) -> tuple[bool, str]:
    """
    Update channel fees via Lightning node API.

    NOTE: This is a placeholder implementation.
    In production, this should use the actual LND/CLN API to update fees.

    Returns: (success, error_message)
    """
    # TODO: Implement actual fee update via Lightning node
    # This would typically use:
    # - LND: UpdateChannelPolicy RPC call
    # - CLN: setchannelfee command

    # For now, simulate success
    logger.info(f"Would update channel {channel_id}: base_fee={base_fee}, fee_rate={fee_rate}")
    return (True, "")


async def process_policy(policy: FeePolicy) -> Dict[str, Any]:
    """
    Process a single policy: fetch channels and adjust fees as needed.

    Returns statistics about the processing.
    """
    stats = {
        "policy_id": policy.id,
        "policy_name": policy.name,
        "channels_processed": 0,
        "adjustments_made": 0,
        "adjustments_failed": 0,
        "errors": [],
    }

    try:
        # Fetch channels for this wallet
        channels = await get_channels_from_wallet(policy.wallet_id)

        for channel in channels:
            # Apply filters
            if policy.only_active_channels and not channel.active:
                continue

            if channel.capacity < policy.min_channel_size:
                continue

            stats["channels_processed"] += 1

            # Calculate optimal fees
            optimal_base_fee, optimal_fee_rate = calculate_optimal_fees(policy, channel)

            # Apply gradual adjustment limit
            optimal_fee_rate = clamp_fee_adjustment(
                policy,
                channel.fee_rate,
                optimal_fee_rate,
            )

            # Check if adjustment is needed
            if not should_adjust_fees(
                policy,
                channel.base_fee,
                channel.fee_rate,
                optimal_base_fee,
                optimal_fee_rate,
            ):
                # No significant change needed
                continue

            # Update fees via Lightning node
            success, error_message = await update_channel_fees(
                policy.wallet_id,
                channel.channel_id,
                optimal_base_fee,
                optimal_fee_rate,
            )

            # Record the adjustment
            reason = get_adjustment_reason(
                policy,
                channel.liquidity_ratio,
                channel.fee_rate,
                optimal_fee_rate,
            )

            adjustment_data = CreateFeeAdjustment(
                policy_id=policy.id,
                channel_id=channel.channel_id,
                old_base_fee=channel.base_fee,
                old_fee_rate=channel.fee_rate,
                new_base_fee=optimal_base_fee,
                new_fee_rate=optimal_fee_rate,
                reason=reason,
                liquidity_ratio=channel.liquidity_ratio,
                success=success,
                error_message=error_message,
            )

            await create_adjustment(adjustment_data)

            if success:
                stats["adjustments_made"] += 1
                logger.info(
                    f"Adjusted fees for channel {channel.channel_id}: "
                    f"{channel.fee_rate} -> {optimal_fee_rate} ppm. Reason: {reason}"
                )
            else:
                stats["adjustments_failed"] += 1
                stats["errors"].append(f"Channel {channel.channel_id}: {error_message}")
                logger.error(
                    f"Failed to adjust fees for channel {channel.channel_id}: {error_message}"
                )

    except Exception as e:
        logger.error(f"Error processing policy {policy.id}: {str(e)}")
        stats["errors"].append(str(e))

    return stats


async def run_autofee_adjustment() -> Dict[str, Any]:
    """
    Main task: Process all enabled policies and adjust fees.

    This should be called periodically (e.g., every hour) to automatically
    adjust channel fees based on configured policies.

    Returns statistics about the run.
    """
    start_time = time.time()

    overall_stats = {
        "start_time": start_time,
        "policies_processed": 0,
        "total_channels_processed": 0,
        "total_adjustments_made": 0,
        "total_adjustments_failed": 0,
        "policy_results": [],
        "duration_seconds": 0,
    }

    try:
        # Get all enabled policies
        policies = await get_enabled_policies()
        logger.info(f"Starting autofee adjustment run with {len(policies)} policies")

        # Process each policy
        for policy in policies:
            policy_stats = await process_policy(policy)
            overall_stats["policies_processed"] += 1
            overall_stats["total_channels_processed"] += policy_stats["channels_processed"]
            overall_stats["total_adjustments_made"] += policy_stats["adjustments_made"]
            overall_stats["total_adjustments_failed"] += policy_stats["adjustments_failed"]
            overall_stats["policy_results"].append(policy_stats)

        end_time = time.time()
        overall_stats["duration_seconds"] = end_time - start_time

        logger.info(
            f"Autofee adjustment completed: "
            f"{overall_stats['total_adjustments_made']} adjustments made, "
            f"{overall_stats['total_adjustments_failed']} failed, "
            f"duration: {overall_stats['duration_seconds']:.2f}s"
        )

    except Exception as e:
        logger.error(f"Error in autofee adjustment run: {str(e)}")
        overall_stats["error"] = str(e)

    return overall_stats


# Helper function for manual triggering
async def trigger_policy_adjustment(policy_id: str) -> Dict[str, Any]:
    """
    Manually trigger fee adjustment for a specific policy.
    Useful for testing or immediate adjustments.
    """
    from .crud import get_policy

    policy = await get_policy(policy_id)
    if not policy:
        return {
            "error": "Policy not found",
            "policy_id": policy_id,
        }

    if not policy.enabled:
        return {
            "error": "Policy is disabled",
            "policy_id": policy_id,
        }

    logger.info(f"Manually triggering adjustment for policy {policy_id}")
    return await process_policy(policy)
