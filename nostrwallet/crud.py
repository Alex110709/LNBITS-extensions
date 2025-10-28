from typing import Optional, List
import time
import secrets
import hashlib
from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import NostrWalletConnection, CreateNostrWalletConnection


async def create_connection(
    data: CreateNostrWalletConnection,
) -> NostrWalletConnection:
    """Create a new Nostr Wallet Connect connection"""
    connection_id = urlsafe_short_hash()

    # Generate Nostr keypair (simplified - in production use proper Nostr library)
    privkey = secrets.token_hex(32)
    pubkey = hashlib.sha256(privkey.encode()).hexdigest()

    # Generate connection secret
    secret = secrets.token_hex(32)

    created_at = int(time.time())

    await db.execute(
        """
        INSERT INTO nostrwallet.connections (
            id, wallet_id, name, nostr_pubkey, nostr_privkey,
            relay_url, secret, permissions, enabled, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            connection_id,
            data.wallet_id,
            data.name,
            pubkey,
            privkey,
            data.relay_url,
            secret,
            data.permissions,
            True,
            created_at,
        ),
    )

    connection = await get_connection(connection_id)
    assert connection, "Newly created connection couldn't be retrieved"
    return connection


async def get_connection(connection_id: str) -> Optional[NostrWalletConnection]:
    """Get a connection by ID"""
    row = await db.fetchone(
        "SELECT * FROM nostrwallet.connections WHERE id = ?",
        (connection_id,),
    )
    return NostrWalletConnection(**row) if row else None


async def get_connections(wallet_id: str) -> List[NostrWalletConnection]:
    """Get all connections for a wallet"""
    rows = await db.fetchall(
        "SELECT * FROM nostrwallet.connections WHERE wallet_id = ?",
        (wallet_id,),
    )
    return [NostrWalletConnection(**row) for row in rows]


async def update_connection(
    connection_id: str,
    name: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Optional[NostrWalletConnection]:
    """Update a connection"""
    updates = []
    params = []

    if name is not None:
        updates.append("name = ?")
        params.append(name)

    if enabled is not None:
        updates.append("enabled = ?")
        params.append(enabled)

    if not updates:
        return await get_connection(connection_id)

    params.append(connection_id)

    await db.execute(
        f"UPDATE nostrwallet.connections SET {', '.join(updates)} WHERE id = ?",
        tuple(params),
    )

    return await get_connection(connection_id)


async def update_last_used(connection_id: str) -> None:
    """Update the last_used_at timestamp"""
    await db.execute(
        "UPDATE nostrwallet.connections SET last_used_at = ? WHERE id = ?",
        (int(time.time()), connection_id),
    )


async def delete_connection(connection_id: str) -> None:
    """Delete a connection"""
    await db.execute(
        "DELETE FROM nostrwallet.connections WHERE id = ?",
        (connection_id,),
    )


async def get_connection_by_pubkey(pubkey: str) -> Optional[NostrWalletConnection]:
    """Get a connection by Nostr public key"""
    row = await db.fetchone(
        "SELECT * FROM nostrwallet.connections WHERE nostr_pubkey = ? AND enabled = ?",
        (pubkey, True),
    )
    return NostrWalletConnection(**row) if row else None
