#!/usr/bin/env python3
"""
Test script for store_accounts function
"""
import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import settings
from src.database.db import get_db
from src.api.plaid.router import store_accounts


def test_store_accounts():
    """Test the store_accounts function with real access token"""

    # Get access token from settings
    access_token = settings.PLAID_ACCESS_TOKEN

    if not access_token:
        print("No PLAID_ACCESS_TOKEN found in environment file")
        print(f"Current environment: {settings.PLAID_ENV}")
        return

    print(f"Access token found: {access_token[:10]}...")
    print(f"Environment: {settings.PLAID_ENV}")
    print(f"Database Schema: {settings.DATABASE_SCHEMA}")

    # Get database session
    try:
        db_gen = get_db()
        db: Session = next(db_gen)
        print("Database connection established")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    # Test store_accounts function
    try:
        print("\nTesting store_accounts function...")
        store_accounts(access_token, db)
        print("store_accounts completed successfully")

        # Verify data was saved
        from src.models.account import Account
        accounts = db.query(Account).all()
        print(f"Accounts in database: {len(accounts)}")

        for account in accounts:
            print(f"  - {account.account_id}: {account.account_name} ({account.account_type})")

    except Exception as e:
        print(f"store_accounts failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_store_accounts()
