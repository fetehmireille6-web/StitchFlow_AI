# fix_database.py
import sqlite3
import os

def fix_database():
    # Path to your database
    db_path = os.path.join(os.path.dirname(__file__), "stitchflow.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   Starting server will create a new database.")
        return
    
    print(f"🔧 Fixing database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ============================================
    # 1. ADD MISSING COLUMNS TO EXISTING TABLES
    # ============================================
    
    print("\n📋 Checking and adding missing columns...")
    
    # Add user_id to customers table
    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN user_id INTEGER")
        print("✅ Added user_id column to customers table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ user_id column already exists in customers table")
        else:
            print(f"⚠️ Could not add user_id: {e}")
    
    # Add user_id to orders table
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN user_id INTEGER")
        print("✅ Added user_id column to orders table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ user_id column already exists in orders table")
        else:
            print(f"⚠️ Could not add user_id: {e}")
    
    # Add garment_type to orders table
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN garment_type TEXT DEFAULT 'general'")
        print("✅ Added garment_type column to orders table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ garment_type column already exists in orders table")
        else:
            print(f"⚠️ Could not add garment_type: {e}")
    
    # ============================================
    # 2. UPDATE EXISTING RECORDS WITH USER_ID
    # ============================================
    
    print("\n👤 Updating existing records with user_id...")
    
    # Get the first user ID (or create default)
    cursor.execute("SELECT id FROM users LIMIT 1")
    first_user = cursor.fetchone()
    
    if first_user:
        default_user_id = first_user[0]
        print(f"   Found existing user with ID: {default_user_id}")
    else:
        # Create a default user if none exists
        default_user_id = 1
        try:
            cursor.execute("INSERT INTO users (id, name, email, password) VALUES (1, 'Admin', 'admin@stitchflow.com', 'admin123')")
            print("   Created default admin user")
        except:
            print("   Default user already exists or cannot be created")
    
    # Update orders without user_id
    cursor.execute(f"UPDATE orders SET user_id = {default_user_id} WHERE user_id IS NULL")
    updated_orders = cursor.rowcount
    print(f"   ✅ Updated {updated_orders} orders with user_id = {default_user_id}")
    
    # Update customers without user_id
    cursor.execute(f"UPDATE customers SET user_id = {default_user_id} WHERE user_id IS NULL")
    updated_customers = cursor.rowcount
    print(f"   ✅ Updated {updated_customers} customers with user_id = {default_user_id}")
    
    # ============================================
    # 3. FIX UNIQUE CONSTRAINT ON CUSTOMERS
    # ============================================
    
    print("\n🔧 Fixing unique constraint on customers table...")
    
    # Check current constraint
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='customers'")
    table_info = cursor.fetchone()
    print(f"   Current schema: {table_info[0][:100]}...")
    
    # Check if we need to recreate the table
    cursor.execute("PRAGMA index_list('customers')")
    indexes = cursor.fetchall()
    
    need_recreate = True
    for idx in indexes:
        cursor.execute(f"PRAGMA index_info('{idx[1]}')")
        columns = cursor.fetchall()
        column_names = [col[2] for col in columns]
        if 'name' in column_names and 'user_id' in column_names:
            need_recreate = False
            print("   ✅ Composite unique constraint (name, user_id) already exists")
            break
    
    if need_recreate:
        print("   Recreating customers table with composite unique constraint...")
        
        # Backup existing data
        cursor.execute("CREATE TABLE customers_backup AS SELECT * FROM customers")
        backup_count = cursor.rowcount
        print(f"   📦 Backed up {backup_count} customers")
        
        # Get column names
        cursor.execute("PRAGMA table_info(customers)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Create new table with composite unique constraint
        cursor.execute("""
            CREATE TABLE customers_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                user_id INTEGER NOT NULL,
                UNIQUE(name, user_id)
            )
        """)
        print("   ✅ Created new table with composite UNIQUE(name, user_id)")
        
        # Copy data, handling duplicates
        cursor.execute("""
            INSERT INTO customers_new (id, name, phone, user_id)
            SELECT MIN(id), name, phone, user_id 
            FROM customers 
            GROUP BY name, user_id
        """)
        copied_count = cursor.rowcount
        print(f"   📋 Copied {copied_count} customers (removed duplicates)")
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE customers")
        cursor.execute("ALTER TABLE customers_new RENAME TO customers")
        print("   ✅ Replaced old customers table")
        
        # Update orders to reference correct customer IDs
        cursor.execute("""
            UPDATE orders 
            SET customer_id = (
                SELECT MIN(c2.id) 
                FROM customers c2 
                WHERE c2.name = (
                    SELECT name FROM customers c1 WHERE c1.id = orders.customer_id
                )
                AND c2.user_id = orders.user_id
            )
            WHERE EXISTS (SELECT 1 FROM customers c1 WHERE c1.id = orders.customer_id)
        """)
        print("   ✅ Updated order references")
    
    # ============================================
    # 4. VERIFY FINAL STRUCTURE
    # ============================================
    
    print("\n📊 Verifying final database structure...")
    
    # Check customers table
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='customers'")
    customers_schema = cursor.fetchone()
    print(f"   Customers table: {customers_schema[0][:80]}...")
    
    # Check orders table
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='orders'")
    orders_schema = cursor.fetchone()
    print(f"   Orders table: {orders_schema[0][:80]}...")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    
    print(f"\n📈 Database Summary:")
    print(f"   👤 Users: {user_count}")
    print(f"   👥 Customers: {customer_count}")
    print(f"   📦 Orders: {order_count}")
    
    # ============================================
    # 5. COMMIT CHANGES
    # ============================================
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database fix completed successfully!")
    print("   You can now restart your server and create orders.")

if __name__ == "__main__":
    print("=" * 50)
    print("   STITCHFLOW DATABASE FIX TOOL")
    print("=" * 50)
    
    # Ask for confirmation
    response = input("\n⚠️  This will modify your database. Continue? (y/n): ")
    if response.lower() == 'y':
        fix_database()
    else:
        print("Operation cancelled.")