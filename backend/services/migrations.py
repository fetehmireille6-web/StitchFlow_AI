from sqlalchemy import text
from services.database import engine

def run_migrations():
    """Add missing columns to existing tables for SQLite"""
    with engine.connect() as conn:
        # Add 'phone' column to 'customers' table
        try:
            conn.execute(text("ALTER TABLE customers ADD COLUMN phone TEXT"))
            conn.commit()
            print("✅ Added 'phone' column to customers table")
        except Exception:
            # Column already exists
            pass

        # Add 'garment_type' column to 'orders' table
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN garment_type TEXT DEFAULT 'general'"))
            conn.commit()
            print("✅ Added 'garment_type' column to orders table")
        except Exception:
            # Column already exists
            pass

    print("✅ Database migration check completed")