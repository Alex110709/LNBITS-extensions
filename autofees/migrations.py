async def m001_initial(db):
    """
    Initial autofees tables.
    """
    # Fee policies table
    await db.execute(
        """
        CREATE TABLE autofees.policies (
            id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            name TEXT NOT NULL,
            enabled BOOLEAN NOT NULL DEFAULT true,
            strategy TEXT NOT NULL,
            base_fee_min INTEGER NOT NULL DEFAULT 0,
            base_fee_max INTEGER NOT NULL DEFAULT 10000,
            base_fee_default INTEGER NOT NULL DEFAULT 1000,
            fee_rate_min INTEGER NOT NULL DEFAULT 1,
            fee_rate_max INTEGER NOT NULL DEFAULT 5000,
            fee_rate_default INTEGER NOT NULL DEFAULT 500,
            liquidity_threshold_low INTEGER NOT NULL DEFAULT 20,
            liquidity_threshold_high INTEGER NOT NULL DEFAULT 80,
            auto_adjust BOOLEAN NOT NULL DEFAULT true,
            adjustment_interval INTEGER NOT NULL DEFAULT 3600,
            max_adjustment_per_step INTEGER NOT NULL DEFAULT 100,
            min_channel_size INTEGER NOT NULL DEFAULT 0,
            only_active_channels BOOLEAN NOT NULL DEFAULT true,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );
        """
    )

    # Fee adjustments history table
    await db.execute(
        """
        CREATE TABLE autofees.adjustments (
            id TEXT PRIMARY KEY,
            policy_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            old_base_fee INTEGER NOT NULL,
            old_fee_rate INTEGER NOT NULL,
            new_base_fee INTEGER NOT NULL,
            new_fee_rate INTEGER NOT NULL,
            reason TEXT NOT NULL,
            liquidity_ratio REAL NOT NULL,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (policy_id) REFERENCES autofees.policies (id)
        );
        """
    )

    # Create indexes
    await db.execute(
        """
        CREATE INDEX idx_autofees_policies_wallet_id
        ON autofees.policies (wallet_id);
        """
    )

    await db.execute(
        """
        CREATE INDEX idx_autofees_adjustments_policy_id
        ON autofees.adjustments (policy_id);
        """
    )

    await db.execute(
        """
        CREATE INDEX idx_autofees_adjustments_timestamp
        ON autofees.adjustments (timestamp);
        """
    )
