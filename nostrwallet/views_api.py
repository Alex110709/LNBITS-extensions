from typing import List
import json
from fastapi import APIRouter, HTTPException, Depends
from lnbits.core.crud import get_user, get_wallet
from lnbits.core.services import create_invoice, pay_invoice
from lnbits.decorators import require_admin_key, require_invoice_key
from lnbits.core.models import WalletTypeInfo

from . import nostrwallet_ext
from .crud import (
    create_connection,
    get_connection,
    get_connections,
    update_connection,
    delete_connection,
    update_last_used,
)
from .models import CreateNostrWalletConnection, NostrWalletConnection


@nostrwallet_ext.post("/api/v1/connections")
async def api_create_connection(
    data: CreateNostrWalletConnection,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> NostrWalletConnection:
    """Create a new Nostr Wallet Connect connection"""
    data.wallet_id = wallet.wallet.id
    return await create_connection(data)


@nostrwallet_ext.get("/api/v1/connections")
async def api_get_connections(
    wallet: WalletTypeInfo = Depends(require_invoice_key),
) -> List[NostrWalletConnection]:
    """Get all connections for the wallet"""
    return await get_connections(wallet.wallet.id)


@nostrwallet_ext.get("/api/v1/connections/{connection_id}")
async def api_get_connection(
    connection_id: str,
    wallet: WalletTypeInfo = Depends(require_invoice_key),
) -> NostrWalletConnection:
    """Get a specific connection"""
    connection = await get_connection(connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your connection")

    return connection


@nostrwallet_ext.put("/api/v1/connections/{connection_id}")
async def api_update_connection(
    connection_id: str,
    name: str = None,
    enabled: bool = None,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> NostrWalletConnection:
    """Update a connection"""
    connection = await get_connection(connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your connection")

    updated = await update_connection(connection_id, name=name, enabled=enabled)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update connection")

    return updated


@nostrwallet_ext.delete("/api/v1/connections/{connection_id}")
async def api_delete_connection(
    connection_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    """Delete a connection"""
    connection = await get_connection(connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=403, detail="Not your connection")

    await delete_connection(connection_id)
    return {"success": True}


@nostrwallet_ext.post("/api/v1/nip47/request")
async def api_nip47_request(
    event: dict,
) -> dict:
    """
    Process NIP-47 request
    This endpoint receives encrypted Nostr events and processes wallet commands
    """
    try:
        # Extract event data
        pubkey = event.get("pubkey")
        content = event.get("content")

        if not pubkey or not content:
            raise HTTPException(status_code=400, detail="Invalid event format")

        # Get connection by pubkey
        from .crud import get_connection_by_pubkey

        connection = await get_connection_by_pubkey(pubkey)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Update last used timestamp
        await update_last_used(connection.id)

        # In a real implementation, you would:
        # 1. Decrypt the content using the connection's keys
        # 2. Parse the JSON-RPC request
        # 3. Check permissions
        # 4. Execute the requested method
        # 5. Encrypt and return the response

        # For now, return a basic response structure
        response = {
            "result_type": "success",
            "result": {
                "message": "NIP-47 handler - implementation in progress"
            },
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@nostrwallet_ext.get("/api/v1/info/{connection_id}")
async def api_get_connection_info(
    connection_id: str,
) -> dict:
    """Get connection string for a connection (public endpoint)"""
    connection = await get_connection(connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Generate nostr+walletconnect:// URI
    uri = f"nostr+walletconnect://{connection.nostr_pubkey}?relay={connection.relay_url}&secret={connection.secret}"

    return {
        "connection_string": uri,
        "pubkey": connection.nostr_pubkey,
        "relay": connection.relay_url,
        "permissions": json.loads(connection.permissions),
    }
