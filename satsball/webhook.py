from fastapi import HTTPException
from .crud import get_stack, get_bet, get_bet_by_payment_hash
from .utils import process_bet_payment

async def handle_payment_webhook(payment_hash: str) -> dict:
    """
    Handle payment webhook from satspay.
    """
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

# The function is now properly imported from crud.py