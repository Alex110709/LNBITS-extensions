import random
from typing import Optional
from .crud import (
    increment_stack_amount, reset_stack_amount, 
    update_bet_as_winner, create_win_history
)
from .models import Stack, Bet

async def process_bet_payment(stack: Stack, bet: Bet) -> dict:
    """
    Process a successful bet payment.
    Returns a dictionary with the result of the bet.
    """
    # Calculate fee and amount to add to stack
    fee = int(bet.amount * (stack.fee_percentage / 100))
    stack_amount = bet.amount - fee
    
    # Add amount to stack (fee goes to admin wallet in real implementation)
    updated_stack = await increment_stack_amount(stack.id, stack_amount)
    
    # Check if this bet wins
    is_winner = check_winning_condition(stack.winning_probability)
    
    result = {
        "is_winner": is_winner,
        "stack_amount": updated_stack.current_amount if updated_stack else stack.current_amount + stack_amount,
        "fee_collected": fee
    }
    
    if is_winner:
        # Mark bet as winner
        await update_bet_as_winner(bet.id)
        
        # Record win in history
        await create_win_history(
            stack_id=stack.id,
            bet_id=bet.id,
            amount_won=updated_stack.current_amount if updated_stack else stack.current_amount + stack_amount,
            user_id=bet.user_id
        )
        
        # Reset stack amount
        await reset_stack_amount(stack.id)
        
        result["amount_won"] = updated_stack.current_amount if updated_stack else stack.current_amount + stack_amount
    
    return result

def check_winning_condition(probability: float) -> bool:
    """
    Check if the winning condition is met based on probability.
    """
    return random.random() <= probability

async def process_win_condition(stack: Stack, bet: Bet) -> Optional[dict]:
    """
    Process the win condition for a bet.
    Returns win details if the bet wins, None otherwise.
    """
    if check_winning_condition(stack.winning_probability):
        # Transfer accumulated amount to user
        # In a real implementation, this would involve actual wallet transfers
        win_amount = stack.current_amount + bet.amount
        
        # Record the win
        win_record = await create_win_history(
            stack_id=stack.id,
            bet_id=bet.id,
            amount_won=win_amount,
            user_id=bet.user_id
        )
        
        # Reset stack amount
        await reset_stack_amount(stack.id)
        
        return {
            "win_amount": win_amount,
            "win_record": win_record
        }
    
    return None