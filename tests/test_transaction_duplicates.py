#!/usr/bin/env python3
"""
Test script to check for duplicate transaction_ids in the database
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import settings
from src.database.db import get_db
from src.models.transaction import Transaction
from sqlalchemy import func


def test_transaction_duplicates():
    """Check for duplicate transaction_ids in the database"""

    print(f"Environment: {settings.PLAID_ENV}")
    print(f"Database Schema: {settings.DATABASE_SCHEMA}")

    # Get database session
    try:
        db_gen = get_db()
        db = next(db_gen)
        print("Database connection established\n")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    try:
        # Check for duplicate transaction_ids
        print("Checking for duplicate transaction_ids...")
        duplicates = db.query(
            Transaction.transaction_id,
            func.count(Transaction.transaction_id).label('count')
        ).group_by(
            Transaction.transaction_id
        ).having(
            func.count(Transaction.transaction_id) > 1
        ).all()

        if duplicates:
            print(f"\n重複しているtransaction_idが見つかりました:")
            for transaction_id, count in duplicates:
                print(f"  - {transaction_id}: {count}件")

                # Show details of duplicates
                duplicate_records = db.query(Transaction).filter(
                    Transaction.transaction_id == transaction_id
                ).all()

                for record in duplicate_records:
                    print(f"    → account_id: {record.account_id}, "
                          f"date: {record.transaction_date}, "
                          f"amount: {record.amount}, "
                          f"is_removed: {record.is_removed}")
        else:
            print("✓ transaction_idの重複はありません")

        # Check total transaction count
        total_count = db.query(Transaction).count()
        unique_count = db.query(Transaction.transaction_id).distinct().count()
        active_count = db.query(Transaction).filter(Transaction.is_removed == False).count()

        print(f"\n統計:")
        print(f"  合計トランザクション数: {total_count}")
        print(f"  ユニークなtransaction_id数: {unique_count}")
        print(f"  削除されていないトランザクション数: {active_count}")

        if total_count != unique_count:
            print(f"\n警告: 合計数({total_count})とユニーク数({unique_count})が一致しません")

    except Exception as e:
        print(f"Error during check: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_transaction_duplicates()
