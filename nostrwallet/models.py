from typing import Optional
from pydantic import BaseModel


class NostrWalletConnection(BaseModel):
    id: str
    wallet_id: str
    name: str
    nostr_pubkey: str
    relay_url: str
    secret: str
    permissions: str  # JSON string of allowed methods
    enabled: bool = True
    created_at: int
    last_used_at: Optional[int] = None


class CreateNostrWalletConnection(BaseModel):
    wallet_id: str
    name: str
    relay_url: str = "wss://relay.damus.io"
    permissions: str = '["pay_invoice", "get_balance", "get_info", "make_invoice", "lookup_invoice", "list_transactions"]'


class NostrEvent(BaseModel):
    id: str
    pubkey: str
    created_at: int
    kind: int
    tags: list
    content: str
    sig: str
