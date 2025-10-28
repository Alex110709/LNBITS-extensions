async def m001_initial(db):
    """
    Initial nostrwallet tables.
    """
    await db.execute(
        """
        CREATE TABLE nostrwallet.connections (
            id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            name TEXT NOT NULL,
            nostr_pubkey TEXT NOT NULL,
            nostr_privkey TEXT NOT NULL,
            relay_url TEXT NOT NULL,
            secret TEXT NOT NULL,
            permissions TEXT NOT NULL,
            enabled BOOLEAN NOT NULL DEFAULT true,
            created_at INTEGER NOT NULL,
            last_used_at INTEGER
        );
        """
    )

    # Create index on wallet_id for faster lookups
    await db.execute(
        """
        CREATE INDEX idx_nostrwallet_wallet_id
        ON nostrwallet.connections (wallet_id);
        """
    )
