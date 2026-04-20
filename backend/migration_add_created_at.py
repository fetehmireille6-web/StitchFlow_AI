# migrate_add_created_at.py
import sqlite3
import os
from datetime import datetime

def add_created_at_column():
    # Find the database file
    db_path = os.path.join(os.path.dirname(__file__), "stitchflow.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   Starting the server will create a new database.")
        return
    
    print(f"🔧 Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if created_at column already exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'created_at' in column_names:
        print("✅ created_at column already exists!")
    else:
        print("📝 Adding created_at column to orders table...")
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN created_at TIMESTAMP")
            print("✅ Added created_at column")
            
            # Set default values for existing orders
            cursor.execute("UPDATE orders SET created_at = datetime('now') WHERE created_at IS NULL")
            print("✅ Set default created_at for existing orders")
            
        except sqlite3.OperationalError as e:
            print(f"⚠️ Error: {e}")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(orders)")
    columns = cursor.fetchall()
    print("\n📋 Current orders table columns:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("   You can now restart your server.")

if __name__ == "__main__":
    print("=" * 50)
    print("   STITCHFLOW DATABASE MIGRATION")
    print("   Adding created_at column to orders")
    print("=" * 50)
    add_created_at_column()