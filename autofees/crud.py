from typing import Optional, List
import time
from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import (
    FeePolicy,
    CreateFeePolicy,
    FeeAdjustment,
    CreateFeeAdjustment,
)


# Fee Policy CRUD operations

async def create_policy(data: CreateFeePolicy) -> FeePolicy:
    """Create a new fee policy"""
    policy_id = urlsafe_short_hash()
    now = int(time.time())

    await db.execute(
        """
        INSERT INTO autofees.policies (
            id, wallet_id, name, enabled, strategy,
            base_fee_min, base_fee_max, base_fee_default,
            fee_rate_min, fee_rate_max, fee_rate_default,
            liquidity_threshold_low, liquidity_threshold_high,
            auto_adjust, adjustment_interval, max_adjustment_per_step,
            min_channel_size, only_active_channels,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            policy_id,
            data.wallet_id,
            data.name,
            True,
            data.strategy,
            data.base_fee_min,
            data.base_fee_max,
            data.base_fee_default,
            data.fee_rate_min,
            data.fee_rate_max,
            data.fee_rate_default,
            data.liquidity_threshold_low,
            data.liquidity_threshold_high,
            data.auto_adjust,
            data.adjustment_interval,
            data.max_adjustment_per_step,
            data.min_channel_size,
            data.only_active_channels,
            now,
            now,
        ),
    )

    policy = await get_policy(policy_id)
    assert policy, "Newly created policy couldn't be retrieved"
    return policy


async def get_policy(policy_id: str) -> Optional[FeePolicy]:
    """Get a policy by ID"""
    row = await db.fetchone(
        "SELECT * FROM autofees.policies WHERE id = ?",
        (policy_id,),
    )
    return FeePolicy(**row) if row else None


async def get_policies(wallet_id: str) -> List[FeePolicy]:
    """Get all policies for a wallet"""
    rows = await db.fetchall(
        "SELECT * FROM autofees.policies WHERE wallet_id = ? ORDER BY created_at DESC",
        (wallet_id,),
    )
    return [FeePolicy(**row) for row in rows]


async def get_enabled_policies() -> List[FeePolicy]:
    """Get all enabled policies (for background processing)"""
    rows = await db.fetchall(
        "SELECT * FROM autofees.policies WHERE enabled = ? AND auto_adjust = ?",
        (True, True),
    )
    return [FeePolicy(**row) for row in rows]


async def update_policy(
    policy_id: str,
    **kwargs,
) -> Optional[FeePolicy]:
    """Update a policy"""
    updates = []
    params = []

    # Add updated_at timestamp
    kwargs["updated_at"] = int(time.time())

    for key, value in kwargs.items():
        if value is not None:
            updates.append(f"{key} = ?")
            params.append(value)

    if not updates:
        return await get_policy(policy_id)

    params.append(policy_id)

    await db.execute(
        f"UPDATE autofees.policies SET {', '.join(updates)} WHERE id = ?",
        tuple(params),
    )

    return await get_policy(policy_id)


async def delete_policy(policy_id: str) -> None:
    """Delete a policy and its adjustments"""
    # Delete related adjustments first
    await db.execute(
        "DELETE FROM autofees.adjustments WHERE policy_id = ?",
        (policy_id,),
    )

    # Delete policy
    await db.execute(
        "DELETE FROM autofees.policies WHERE id = ?",
        (policy_id,),
    )


# Fee Adjustment CRUD operations

async def create_adjustment(data: CreateFeeAdjustment) -> FeeAdjustment:
    """Record a fee adjustment"""
    adjustment_id = urlsafe_short_hash()
    timestamp = int(time.time())

    await db.execute(
        """
        INSERT INTO autofees.adjustments (
            id, policy_id, channel_id,
            old_base_fee, old_fee_rate,
            new_base_fee, new_fee_rate,
            reason, liquidity_ratio,
            success, error_message,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            adjustment_id,
            data.policy_id,
            data.channel_id,
            data.old_base_fee,
            data.old_fee_rate,
            data.new_base_fee,
            data.new_fee_rate,
            data.reason,
            data.liquidity_ratio,
            data.success,
            data.error_message,
            timestamp,
        ),
    )

    adjustment = await get_adjustment(adjustment_id)
    assert adjustment, "Newly created adjustment couldn't be retrieved"
    return adjustment


async def get_adjustment(adjustment_id: str) -> Optional[FeeAdjustment]:
    """Get an adjustment by ID"""
    row = await db.fetchone(
        "SELECT * FROM autofees.adjustments WHERE id = ?",
        (adjustment_id,),
    )
    return FeeAdjustment(**row) if row else None


async def get_adjustments_by_policy(
    policy_id: str,
    limit: int = 100,
) -> List[FeeAdjustment]:
    """Get adjustments for a policy"""
    rows = await db.fetchall(
        """
        SELECT * FROM autofees.adjustments
        WHERE policy_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (policy_id, limit),
    )
    return [FeeAdjustment(**row) for row in rows]


async def get_adjustments_by_channel(
    channel_id: str,
    limit: int = 100,
) -> List[FeeAdjustment]:
    """Get adjustments for a specific channel"""
    rows = await db.fetchall(
        """
        SELECT * FROM autofees.adjustments
        WHERE channel_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (channel_id, limit),
    )
    return [FeeAdjustment(**row) for row in rows]


async def get_recent_adjustments(
    wallet_id: str,
    limit: int = 50,
) -> List[FeeAdjustment]:
    """Get recent adjustments for a wallet"""
    rows = await db.fetchall(
        """
        SELECT a.* FROM autofees.adjustments a
        JOIN autofees.policies p ON a.policy_id = p.id
        WHERE p.wallet_id = ?
        ORDER BY a.timestamp DESC
        LIMIT ?
        """,
        (wallet_id, limit),
    )
    return [FeeAdjustment(**row) for row in rows]


async def get_adjustment_stats(policy_id: str) -> dict:
    """Get statistics for a policy's adjustments"""
    row = await db.fetchone(
        """
        SELECT
            COUNT(*) as total_adjustments,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_adjustments,
            SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_adjustments,
            AVG(new_fee_rate - old_fee_rate) as avg_fee_rate_change,
            MIN(timestamp) as first_adjustment,
            MAX(timestamp) as last_adjustment
        FROM autofees.adjustments
        WHERE policy_id = ?
        """,
        (policy_id,),
    )

    if row:
        return {
            "total_adjustments": row["total_adjustments"] or 0,
            "successful_adjustments": row["successful_adjustments"] or 0,
            "failed_adjustments": row["failed_adjustments"] or 0,
            "avg_fee_rate_change": row["avg_fee_rate_change"] or 0.0,
            "first_adjustment": row["first_adjustment"],
            "last_adjustment": row["last_adjustment"],
        }

    return {
        "total_adjustments": 0,
        "successful_adjustments": 0,
        "failed_adjustments": 0,
        "avg_fee_rate_change": 0.0,
        "first_adjustment": None,
        "last_adjustment": None,
    }
