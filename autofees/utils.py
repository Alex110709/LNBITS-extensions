from typing import Tuple
from .models import FeePolicy, ChannelInfo


def calculate_liquidity_ratio(local_balance: int, capacity: int) -> float:
    """Calculate the liquidity ratio (local balance / capacity)"""
    if capacity == 0:
        return 0.0
    return (local_balance / capacity) * 100


def calculate_optimal_fees(
    policy: FeePolicy,
    channel: ChannelInfo,
) -> Tuple[int, int]:
    """
    Calculate optimal fees based on policy and channel state.
    Returns (base_fee, fee_rate) tuple.

    Strategy logic:
    - Low liquidity (< threshold_low): Increase fees to discourage outbound
    - High liquidity (> threshold_high): Decrease fees to encourage outbound
    - Balanced: Use default fees
    """
    liquidity_ratio = channel.liquidity_ratio

    if policy.strategy == "balanced":
        return _calculate_balanced_fees(policy, liquidity_ratio)
    elif policy.strategy == "aggressive":
        return _calculate_aggressive_fees(policy, liquidity_ratio)
    elif policy.strategy == "conservative":
        return _calculate_conservative_fees(policy, liquidity_ratio)
    else:
        # Default to balanced for unknown strategies
        return _calculate_balanced_fees(policy, liquidity_ratio)


def _calculate_balanced_fees(policy: FeePolicy, liquidity_ratio: float) -> Tuple[int, int]:
    """
    Balanced strategy: Moderate fee adjustments based on liquidity.

    - Very low liquidity (< low_threshold): High fees (80-100% of max)
    - Low liquidity (low_threshold to 40%): Medium-high fees (60-80% of max)
    - Balanced (40-60%): Default fees
    - High liquidity (60% to high_threshold): Medium-low fees (40-60% of max)
    - Very high liquidity (> high_threshold): Low fees (20-40% of max)
    """
    base_fee_range = policy.base_fee_max - policy.base_fee_min
    fee_rate_range = policy.fee_rate_max - policy.fee_rate_min

    if liquidity_ratio < policy.liquidity_threshold_low:
        # Very low liquidity - high fees
        ratio = (policy.liquidity_threshold_low - liquidity_ratio) / policy.liquidity_threshold_low
        base_fee = int(policy.base_fee_min + base_fee_range * (0.8 + ratio * 0.2))
        fee_rate = int(policy.fee_rate_min + fee_rate_range * (0.8 + ratio * 0.2))
    elif liquidity_ratio < 40:
        # Low liquidity - medium-high fees
        ratio = (40 - liquidity_ratio) / (40 - policy.liquidity_threshold_low)
        base_fee = int(policy.base_fee_min + base_fee_range * (0.6 + ratio * 0.2))
        fee_rate = int(policy.fee_rate_min + fee_rate_range * (0.6 + ratio * 0.2))
    elif liquidity_ratio <= 60:
        # Balanced - default fees
        base_fee = policy.base_fee_default
        fee_rate = policy.fee_rate_default
    elif liquidity_ratio <= policy.liquidity_threshold_high:
        # High liquidity - medium-low fees
        ratio = (liquidity_ratio - 60) / (policy.liquidity_threshold_high - 60)
        base_fee = int(policy.base_fee_min + base_fee_range * (0.4 - ratio * 0.2))
        fee_rate = int(policy.fee_rate_min + fee_rate_range * (0.4 - ratio * 0.2))
    else:
        # Very high liquidity - low fees
        ratio = min((liquidity_ratio - policy.liquidity_threshold_high) / (100 - policy.liquidity_threshold_high), 1.0)
        base_fee = int(policy.base_fee_min + base_fee_range * (0.4 - ratio * 0.2))
        fee_rate = int(policy.fee_rate_min + fee_rate_range * (0.4 - ratio * 0.2))

    return (base_fee, fee_rate)


def _calculate_aggressive_fees(policy: FeePolicy, liquidity_ratio: float) -> Tuple[int, int]:
    """
    Aggressive strategy: Large fee swings to quickly rebalance.

    - Low liquidity: Maximum fees
    - High liquidity: Minimum fees
    """
    base_fee_range = policy.base_fee_max - policy.base_fee_min
    fee_rate_range = policy.fee_rate_max - policy.fee_rate_min

    if liquidity_ratio < policy.liquidity_threshold_low:
        # Low liquidity - maximum fees
        base_fee = policy.base_fee_max
        fee_rate = policy.fee_rate_max
    elif liquidity_ratio > policy.liquidity_threshold_high:
        # High liquidity - minimum fees
        base_fee = policy.base_fee_min
        fee_rate = policy.fee_rate_min
    else:
        # Linear interpolation between min and max
        ratio = (liquidity_ratio - policy.liquidity_threshold_low) / \
                (policy.liquidity_threshold_high - policy.liquidity_threshold_low)
        base_fee = int(policy.base_fee_max - base_fee_range * ratio)
        fee_rate = int(policy.fee_rate_max - fee_rate_range * ratio)

    return (base_fee, fee_rate)


def _calculate_conservative_fees(policy: FeePolicy, liquidity_ratio: float) -> Tuple[int, int]:
    """
    Conservative strategy: Small fee adjustments around default.

    - Stay close to default fees
    - Make small adjustments only at extremes
    """
    base_fee_range = policy.base_fee_max - policy.base_fee_min
    fee_rate_range = policy.fee_rate_max - policy.fee_rate_min

    if liquidity_ratio < policy.liquidity_threshold_low:
        # Low liquidity - slightly increase fees (up to 30% above default)
        ratio = (policy.liquidity_threshold_low - liquidity_ratio) / policy.liquidity_threshold_low
        adjustment = ratio * 0.3
        base_fee = int(policy.base_fee_default + base_fee_range * adjustment * 0.5)
        fee_rate = int(policy.fee_rate_default + fee_rate_range * adjustment * 0.5)
    elif liquidity_ratio > policy.liquidity_threshold_high:
        # High liquidity - slightly decrease fees (up to 30% below default)
        ratio = (liquidity_ratio - policy.liquidity_threshold_high) / (100 - policy.liquidity_threshold_high)
        adjustment = ratio * 0.3
        base_fee = int(policy.base_fee_default - base_fee_range * adjustment * 0.5)
        fee_rate = int(policy.fee_rate_default - fee_rate_range * adjustment * 0.5)
    else:
        # Normal range - use defaults
        base_fee = policy.base_fee_default
        fee_rate = policy.fee_rate_default

    # Ensure within bounds
    base_fee = max(policy.base_fee_min, min(base_fee, policy.base_fee_max))
    fee_rate = max(policy.fee_rate_min, min(fee_rate, policy.fee_rate_max))

    return (base_fee, fee_rate)


def should_adjust_fees(
    policy: FeePolicy,
    current_base_fee: int,
    current_fee_rate: int,
    new_base_fee: int,
    new_fee_rate: int,
) -> bool:
    """
    Determine if fees should be adjusted based on the change amount.
    Only adjust if the change exceeds the max_adjustment_per_step.
    """
    base_fee_change = abs(new_base_fee - current_base_fee)
    fee_rate_change = abs(new_fee_rate - current_fee_rate)

    # If either change is significant, adjust
    # For base_fee, we check absolute difference
    # For fee_rate, we check ppm difference
    return fee_rate_change >= 10 or base_fee_change >= 100


def clamp_fee_adjustment(
    policy: FeePolicy,
    current_fee_rate: int,
    target_fee_rate: int,
) -> int:
    """
    Clamp fee rate adjustment to max_adjustment_per_step.
    This ensures gradual changes rather than sudden jumps.
    """
    change = target_fee_rate - current_fee_rate
    max_change = policy.max_adjustment_per_step

    if abs(change) <= max_change:
        return target_fee_rate

    if change > 0:
        return current_fee_rate + max_change
    else:
        return current_fee_rate - max_change


def get_adjustment_reason(
    policy: FeePolicy,
    liquidity_ratio: float,
    old_fee_rate: int,
    new_fee_rate: int,
) -> str:
    """Generate a human-readable reason for the fee adjustment"""
    if liquidity_ratio < policy.liquidity_threshold_low:
        direction = "increased" if new_fee_rate > old_fee_rate else "adjusted"
        return f"Low liquidity ({liquidity_ratio:.1f}%) - fees {direction} to discourage outbound"
    elif liquidity_ratio > policy.liquidity_threshold_high:
        direction = "decreased" if new_fee_rate < old_fee_rate else "adjusted"
        return f"High liquidity ({liquidity_ratio:.1f}%) - fees {direction} to encourage outbound"
    else:
        return f"Balanced liquidity ({liquidity_ratio:.1f}%) - fees set to optimal level"
