from typing import Optional
from pydantic import BaseModel


class FeePolicy(BaseModel):
    """Fee adjustment policy configuration"""
    id: str
    wallet_id: str
    name: str
    enabled: bool = True

    # Strategy type
    strategy: str  # "balanced", "aggressive", "conservative", "custom"

    # Base fee settings (in millisatoshis)
    base_fee_min: int = 0
    base_fee_max: int = 10000
    base_fee_default: int = 1000

    # Fee rate settings (in ppm - parts per million)
    fee_rate_min: int = 1
    fee_rate_max: int = 5000
    fee_rate_default: int = 500

    # Adjustment triggers
    liquidity_threshold_low: int = 20  # % - when local balance is low
    liquidity_threshold_high: int = 80  # % - when local balance is high

    # Auto-adjustment settings
    auto_adjust: bool = True
    adjustment_interval: int = 3600  # seconds between adjustments
    max_adjustment_per_step: int = 100  # max ppm change per adjustment

    # Channel filters
    min_channel_size: int = 0  # minimum channel capacity in sats
    only_active_channels: bool = True

    created_at: int
    updated_at: int


class CreateFeePolicy(BaseModel):
    wallet_id: str
    name: str
    strategy: str = "balanced"
    base_fee_min: int = 0
    base_fee_max: int = 10000
    base_fee_default: int = 1000
    fee_rate_min: int = 1
    fee_rate_max: int = 5000
    fee_rate_default: int = 500
    liquidity_threshold_low: int = 20
    liquidity_threshold_high: int = 80
    auto_adjust: bool = True
    adjustment_interval: int = 3600
    max_adjustment_per_step: int = 100
    min_channel_size: int = 0
    only_active_channels: bool = True


class FeeAdjustment(BaseModel):
    """Record of a fee adjustment"""
    id: str
    policy_id: str
    channel_id: str

    # Previous values
    old_base_fee: int
    old_fee_rate: int

    # New values
    new_base_fee: int
    new_fee_rate: int

    # Reason for adjustment
    reason: str
    liquidity_ratio: float

    # Result
    success: bool
    error_message: Optional[str] = None

    timestamp: int


class ChannelInfo(BaseModel):
    """Channel information snapshot"""
    channel_id: str
    peer_id: str
    capacity: int
    local_balance: int
    remote_balance: int
    base_fee: int
    fee_rate: int
    active: bool
    liquidity_ratio: float  # local_balance / capacity
    last_updated: int


class CreateFeeAdjustment(BaseModel):
    policy_id: str
    channel_id: str
    old_base_fee: int
    old_fee_rate: int
    new_base_fee: int
    new_fee_rate: int
    reason: str
    liquidity_ratio: float
    success: bool
    error_message: Optional[str] = None
