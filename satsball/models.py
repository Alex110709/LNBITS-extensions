from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Stack models
class Stack(BaseModel):
    id: str
    name: str
    description: str
    current_amount: int
    bet_price: int
    winning_probability: float
    fee_percentage: float
    enabled: bool
    created_at: datetime


class CreateStackData(BaseModel):
    name: str
    description: str
    bet_price: int
    winning_probability: float
    fee_percentage: float
    enabled: bool = True


class UpdateStackData(BaseModel):
    name: Optional[str]
    description: Optional[str]
    bet_price: Optional[int]
    winning_probability: Optional[float]
    fee_percentage: Optional[float]
    enabled: Optional[bool]


# Bet models
class Bet(BaseModel):
    id: str
    stack_id: str
    payment_hash: str
    amount: int
    user_id: Optional[str]
    created_at: datetime
    is_winner: bool


class CreateBetData(BaseModel):
    stack_id: str
    amount: int
    user_id: Optional[str] = None


# Win History models
class WinHistory(BaseModel):
    id: str
    stack_id: str
    bet_id: str
    amount_won: int
    user_id: Optional[str]
    timestamp: datetime


# API response models
class StackResponse(Stack):
    pass


class BetResponse(Bet):
    pass


class WinHistoryResponse(WinHistory):
    pass


class stacksResponse(BaseModel):
    stacks: List[StackResponse]


class BetsResponse(BaseModel):
    bets: List[BetResponse]


class WinHistoryListResponse(BaseModel):
    history: List[WinHistoryResponse]