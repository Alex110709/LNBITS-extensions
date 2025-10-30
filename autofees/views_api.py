from typing import List
from fastapi import HTTPException, Depends
from lnbits.decorators import require_admin_key, require_invoice_key
from lnbits.core.models import WalletTypeInfo

from . import autofees_ext
from .crud import (
    create_policy,
    get_policy,
    get_policies,
    update_policy,
    delete_policy,
    get_adjustments_by_policy,
    get_recent_adjustments,
    get_adjustment_stats,
)
from .models import (
    FeePolicy,
    CreateFeePolicy,
    FeeAdjustment,
)
from .tasks import trigger_policy_adjustment


# Policy Management Endpoints

@autofees_ext.post("/api/v1/policies")
async def api_create_policy(
    data: CreateFeePolicy,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> FeePolicy:
    """Create a new fee policy"""
    data.wallet_id = wallet.wallet.id
    return await create_policy(data)


@autofees_ext.get("/api/v1/policies")
async def api_get_policies(
    wallet: WalletTypeInfo = Depends(require_invoice_key),
) -> List[FeePolicy]:
    """Get all policies for the wallet"""
    return await get_policies(wallet.wallet.id)


@autofees_ext.get("/api/v1/policies/{policy_id}")
async def api_get_policy(
    policy_id: str,
    wallet: WalletTypeInfo = Depends(require_invoice_key),
) -> FeePolicy:
    """Get a specific policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    return policy


@autofees_ext.put("/api/v1/policies/{policy_id}")
async def api_update_policy(
    policy_id: str,
    data: dict,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> FeePolicy:
    """Update a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    updated = await update_policy(policy_id, **data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update policy")

    return updated


@autofees_ext.delete("/api/v1/policies/{policy_id}")
async def api_delete_policy(
    policy_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    """Delete a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    await delete_policy(policy_id)
    return {"success": True}


# Policy Actions

@autofees_ext.post("/api/v1/policies/{policy_id}/trigger")
async def api_trigger_policy(
    policy_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    """Manually trigger fee adjustment for a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    result = await trigger_policy_adjustment(policy_id)
    return result


@autofees_ext.post("/api/v1/policies/{policy_id}/enable")
async def api_enable_policy(
    policy_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    """Enable a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    updated = await update_policy(policy_id, enabled=True)
    return updated


@autofees_ext.post("/api/v1/policies/{policy_id}/disable")
async def api_disable_policy(
    policy_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    """Disable a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    updated = await update_policy(policy_id, enabled=False)
    return updated


# Adjustment History Endpoints

@autofees_ext.get("/api/v1/policies/{policy_id}/adjustments")
async def api_get_policy_adjustments(
    policy_id: str,
    limit: int = 100,
    wallet: WalletTypeInfo = Depends(require_invoice_key),
) -> List[FeeAdjustment]:
    """Get adjustment history for a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    return await get_adjustments_by_policy(policy_id, limit)


@autofees_ext.get("/api/v1/adjustments")
async def api_get_recent_adjustments(
    limit: int = 50,
    wallet: WalletTypeInfo = Depends(require_invoice_key),
) -> List[FeeAdjustment]:
    """Get recent adjustments for the wallet"""
    return await get_recent_adjustments(wallet.wallet.id, limit)


@autofees_ext.get("/api/v1/policies/{policy_id}/stats")
async def api_get_policy_stats(
    policy_id: str,
    wallet: WalletTypeInfo = Depends(require_invoice_key),
):
    """Get statistics for a policy"""
    policy = await get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    stats = await get_adjustment_stats(policy_id)
    return {
        "policy_id": policy_id,
        "policy_name": policy.name,
        **stats,
    }


# Utility Endpoints

@autofees_ext.get("/api/v1/strategies")
async def api_get_strategies():
    """Get available fee adjustment strategies"""
    return {
        "strategies": [
            {
                "id": "balanced",
                "name": "Balanced",
                "description": "Moderate fee adjustments to maintain balanced liquidity. Good for most nodes.",
            },
            {
                "id": "aggressive",
                "name": "Aggressive",
                "description": "Large fee swings to quickly rebalance channels. Use with caution.",
            },
            {
                "id": "conservative",
                "name": "Conservative",
                "description": "Small fee adjustments around defaults. Safest option with minimal changes.",
            },
        ]
    }


@autofees_ext.get("/api/v1/defaults")
async def api_get_defaults():
    """Get default policy settings"""
    return {
        "strategy": "balanced",
        "base_fee_min": 0,
        "base_fee_max": 10000,
        "base_fee_default": 1000,
        "fee_rate_min": 1,
        "fee_rate_max": 5000,
        "fee_rate_default": 500,
        "liquidity_threshold_low": 20,
        "liquidity_threshold_high": 80,
        "auto_adjust": True,
        "adjustment_interval": 3600,
        "max_adjustment_per_step": 100,
        "min_channel_size": 0,
        "only_active_channels": True,
    }
