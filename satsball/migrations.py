from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.sql import func
from lnbits.db import Database
from lnbits.db import SQLITE


def m001_initial(db):
    """
    Initial SatsBall tables
    """
    db.execute(
        f"""
        CREATE TABLE satsball.stacks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            current_amount INTEGER NOT NULL DEFAULT 0,
            bet_price INTEGER NOT NULL,
            winning_probability FLOAT NOT NULL,
            fee_percentage FLOAT NOT NULL,
            enabled BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )

    db.execute(
        f"""
        CREATE TABLE satsball.bets (
            id TEXT PRIMARY KEY,
            stack_id TEXT NOT NULL,
            payment_hash TEXT NOT NULL,
            amount INTEGER NOT NULL,
            user_id TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            is_winner BOOLEAN NOT NULL DEFAULT false,
            FOREIGN KEY (stack_id) REFERENCES stacks (id)
        );
    """
    )

    db.execute(
        f"""
        CREATE TABLE satsball.win_history (
            id TEXT PRIMARY KEY,
            stack_id TEXT NOT NULL,
            bet_id TEXT NOT NULL,
            amount_won INTEGER NOT NULL,
            user_id TEXT,
            timestamp TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            FOREIGN KEY (stack_id) REFERENCES stacks (id),
            FOREIGN KEY (bet_id) REFERENCES bets (id)
        );
    """
    )