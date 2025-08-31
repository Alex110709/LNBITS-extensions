import secrets
from typing import List, Optional
from datetime import datetime

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import Stack, Bet, WinHistory, CreateStackData, UpdateStackData

# Stack CRUD operations
async def create_stack(data: CreateStackData) -> Stack:
    stack_id = urlsafe_short_hash()
    stack = Stack(
        id=stack_id,
        name=data.name,
        description=data.description,
        current_amount=0,
        bet_price=data.bet_price,
        winning_probability=data.winning_probability,
        fee_percentage=data.fee_percentage,
        enabled=data.enabled
    )
    await db.insert("satsball.stacks", stack)
    return stack

async def get_stack(stack_id: str) -> Optional[Stack]:
    return await db.fetchone("SELECT * FROM satsball.stacks WHERE id = :id", {"id": stack_id}, Stack)

async def get_stacks(enabled_only: bool = True) -> List[Stack]:
    query = "SELECT * FROM satsball.stacks"
    if enabled_only:
        query += " WHERE enabled = true"
    query += " ORDER BY created_at DESC"
    return await db.fetchall(query, model=Stack)

async def update_stack(stack_id: str, data: UpdateStackData) -> Optional[Stack]:
    q = "UPDATE satsball.stacks SET"
    values = {"id": stack_id}
    
    updates = []
    for field, value in data.dict(exclude_unset=True).items():
        updates.append(f" {field} = :{field}")
        values[field] = value
    
    if not updates:
        return await get_stack(stack_id)
        
    q += ",".join(updates)
    q += " WHERE id = :id"
    
    await db.execute(q, values)
    return await get_stack(stack_id)

async def delete_stack(stack_id: str) -> bool:
    await db.execute("DELETE FROM satsball.stacks WHERE id = :id", {"id": stack_id})
    return True

# Bet CRUD operations
async def create_bet(stack_id: str, payment_hash: str, amount: int, user_id: Optional[str] = None) -> Bet:
    bet_id = urlsafe_short_hash()
    bet = Bet(
        id=bet_id,
        stack_id=stack_id,
        payment_hash=payment_hash,
        amount=amount,
        user_id=user_id,
        is_winner=False
    )
    await db.insert("satsball.bets", bet)
    return bet

async def get_bet(bet_id: str) -> Optional[Bet]:
    return await db.fetchone("SELECT * FROM satsball.bets WHERE id = :id", {"id": bet_id}, Bet)

async def get_bet_by_payment_hash(payment_hash: str) -> Optional[Bet]:
    return await db.fetchone("SELECT * FROM satsball.bets WHERE payment_hash = :payment_hash", {"payment_hash": payment_hash}, Bet)

async def get_bets_by_stack(stack_id: str) -> List[Bet]:
    return await db.fetchall(
        "SELECT * FROM satsball.bets WHERE stack_id = :stack_id ORDER BY created_at DESC",
        {"stack_id": stack_id},
        Bet
    )

async def update_bet_as_winner(bet_id: str) -> Optional[Bet]:
    await db.execute(
        "UPDATE satsball.bets SET is_winner = true WHERE id = :id",
        {"id": bet_id}
    )
    return await get_bet(bet_id)

# Win History CRUD operations
async def create_win_history(stack_id: str, bet_id: str, amount_won: int, user_id: Optional[str] = None) -> WinHistory:
    win_id = urlsafe_short_hash()
    win = WinHistory(
        id=win_id,
        stack_id=stack_id,
        bet_id=bet_id,
        amount_won=amount_won,
        user_id=user_id,
        timestamp=datetime.utcnow()
    )
    await db.insert("satsball.win_history", win)
    return win

async def get_win_history(stack_id: str) -> List[WinHistory]:
    return await db.fetchall(
        "SELECT * FROM satsball.win_history WHERE stack_id = :stack_id ORDER BY timestamp DESC",
        {"stack_id": stack_id},
        WinHistory
    )

async def get_all_win_history() -> List[WinHistory]:
    return await db.fetchall(
        "SELECT * FROM satsball.win_history ORDER BY timestamp DESC",
        model=WinHistory
    )

# Stack amount operations
async def increment_stack_amount(stack_id: str, amount: int) -> Optional[Stack]:
    await db.execute(
        "UPDATE satsball.stacks SET current_amount = current_amount + :amount WHERE id = :id",
        {"id": stack_id, "amount": amount}
    )
    return await get_stack(stack_id)

async def reset_stack_amount(stack_id: str) -> Optional[Stack]:
    await db.execute(
        "UPDATE satsball.stacks SET current_amount = 0 WHERE id = :id",
        {"id": stack_id}
    )
    return await get_stack(stack_id)