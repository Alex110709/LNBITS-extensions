import secrets
import random
from fastapi import Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from lnbits.core.models import User, WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key
from lnbits.extensions.satspay.models import CreateCharge
from lnbits.extensions.satspay.crud import create_charge, get_charge
from lnbits.helpers import urlsafe_short_hash

from . import satsball_ext
from .crud import (
    create_stack, get_stack, get_stacks, update_stack, delete_stack,
    create_bet, get_bet, get_bets_by_stack, update_bet_as_winner,
    create_win_history, get_win_history, get_all_win_history,
    increment_stack_amount, reset_stack_amount, get_bet_by_payment_hash
)
from .models import (
    CreateStackData, UpdateStackData, StackResponse, 
    BetResponse, WinHistoryResponse
)
from .utils import process_bet_payment

# Public API endpoints
@satsball_ext.get("/api/v1/stacks", response_model=list[StackResponse])
async def api_get_stacks():
    """List all available stacks"""
    stacks = await get_stacks()
    return [StackResponse(**stack.dict()) for stack in stacks]

@satsball_ext.get("/api/v1/stacks/{stack_id}", response_model=StackResponse)
async def api_get_stack(stack_id: str):
    """Get details of a specific stack"""
    stack = await get_stack(stack_id)
    if not stack:
        raise HTTPException(status_code=404, detail="Stack not found")
    return StackResponse(**stack.dict())

@satsball_ext.post("/api/v1/stacks/{stack_id}/bet", response_model=BetResponse)
async def api_place_bet(stack_id: str, request: Request, wallet: WalletTypeInfo = Depends(require_invoice_key)):
    """Place a bet on a stack"""
    stack = await get_stack(stack_id)
    if not stack or not stack.enabled:
        raise HTTPException(status_code=404, detail="Stack not found or disabled")
    
    # Create a charge via satspay
    charge_data = CreateCharge(
        amount=stack.bet_price,
        memo=f"Bet on {stack.name}",
        webhook=urlsafe_short_hash(),  # In a real implementation, this would be a proper webhook URL
        completelink=f"/satsball/payment/success/{stack_id}",
        completelinktext="Return to SatsBall",
        wallet=wallet.wallet.id
    )
    
    charge = await create_charge(charge_data)
    
    # Create a bet record
    bet = await create_bet(stack_id, charge.payment_hash, stack.bet_price)
    
    # Return the payment page URL
    return {"payment_url": f"/satspay/{charge.id}"}

@satsball_ext.get("/api/v1/bets/{bet_id}", response_model=BetResponse)
async def api_get_bet(bet_id: str):
    """Check the status of a bet"""
    bet = await get_bet(bet_id)
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    return BetResponse(**bet.dict())

# Admin API endpoints
@satsball_ext.get("/api/v1/admin/stacks", response_model=list[StackResponse])
async def api_admin_get_stacks(key_info: WalletTypeInfo = Depends(require_admin_key)):
    """List all stacks (admin view)"""
    stacks = await get_stacks(enabled_only=False)
    return [StackResponse(**stack.dict()) for stack in stacks]

@satsball_ext.post("/api/v1/admin/stacks", response_model=StackResponse)
async def api_admin_create_stack(
    data: CreateStackData,
    key_info: WalletTypeInfo = Depends(require_admin_key)
):
    """Create a new stack"""
    stack = await create_stack(data)
    return StackResponse(**stack.dict())

@satsball_ext.put("/api/v1/admin/stacks/{stack_id}", response_model=StackResponse)
async def api_admin_update_stack(
    stack_id: str,
    data: UpdateStackData,
    key_info: WalletTypeInfo = Depends(require_admin_key)
):
    """Update stack configuration"""
    stack = await update_stack(stack_id, data)
    if not stack:
        raise HTTPException(status_code=404, detail="Stack not found")
    return StackResponse(**stack.dict())

@satsball_ext.delete("/api/v1/admin/stacks/{stack_id}")
async def api_admin_delete_stack(
    stack_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key)
):
    """Delete a stack"""
    result = await delete_stack(stack_id)
    if not result:
        raise HTTPException(status_code=404, detail="Stack not found")
    return {"message": "Stack deleted successfully"}

@satsball_ext.get("/api/v1/admin/stacks/{stack_id}/history", response_model=list[WinHistoryResponse])
async def api_admin_get_stack_history(
    stack_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key)
):
    """View win history for a stack"""
    history = await get_win_history(stack_id)
    return [WinHistoryResponse(**win.dict()) for win in history]

@satsball_ext.get("/api/v1/admin/history", response_model=list[WinHistoryResponse])
async def api_admin_get_all_history(
    key_info: WalletTypeInfo = Depends(require_admin_key)
):
    """View all win history"""
    history = await get_all_win_history()
    return [WinHistoryResponse(**win.dict()) for win in history]

@satsball_ext.post("/api/v1/webhook/{payment_hash}")
async def api_payment_webhook(payment_hash: str):
    """Handle payment webhook from satspay"""
    # Get bet by payment hash
    bet = await get_bet_by_payment_hash(payment_hash)
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    
    # Get stack
    stack = await get_stack(bet.stack_id)
    if not stack:
        raise HTTPException(status_code=404, detail="Stack not found")
    
    # Process the bet payment
    result = await process_bet_payment(stack, bet)
    
    return {
        "success": True,
        "bet_id": bet.id,
        "result": result
    }