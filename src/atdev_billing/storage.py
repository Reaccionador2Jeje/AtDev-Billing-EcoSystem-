"""Small SQLite persistence layer for entitlement grants."""
import os
import sqlite3
from pathlib import Path

DEFAULT_DB = "data/atdev_billing.sqlite3"


def database_path() -> str:
    return os.getenv("ATDEV_BILLING_DB", DEFAULT_DB)


def connect():
    path = Path(database_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('active','cancelled','expired')),
            starts_at TEXT NOT NULL,
            expires_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_customer_product
        ON subscriptions(customer_id, product_id, status)
    """)
    db.commit()
    return db


def save_subscription(record: dict):
    with connect() as db:
        db.execute("""
            INSERT INTO subscriptions
            (id, customer_id, product_id, plan_id, status, starts_at, expires_at, created_at)
            VALUES (:id, :customer_id, :product_id, :plan_id, :status, :starts_at, :expires_at, :created_at)
            ON CONFLICT(id) DO UPDATE SET
              plan_id=excluded.plan_id, status=excluded.status,
              starts_at=excluded.starts_at, expires_at=excluded.expires_at
        """, record)


def find_subscription(customer_id: str, product_id: str):
    with connect() as db:
        row = db.execute("""
            SELECT * FROM subscriptions
            WHERE customer_id=? AND product_id=? AND status='active'
            ORDER BY created_at DESC LIMIT 1
        """, (customer_id, product_id)).fetchone()
        return dict(row) if row else None


def cancel_subscription(subscription_id: str) -> bool:
    with connect() as db:
        cursor = db.execute(
            "UPDATE subscriptions SET status='cancelled' WHERE id=? AND status='active'",
            (subscription_id,),
        )
        return cursor.rowcount > 0
