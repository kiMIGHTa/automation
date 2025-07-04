import sqlite3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database(db_name='business_automation.db'):
    """Create and populate the SQLite database"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        logger.info(f"Creating database {db_name}...")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            total_orders INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0.0,
            customer_type TEXT DEFAULT 'Regular'
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            hire_date TEXT NOT NULL,
            sales_target REAL NOT NULL,
            sales_achieved REAL NOT NULL,
            performance_rating REAL,
            region TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            cost REAL,
            stock_quantity INTEGER NOT NULL,
            reorder_level INTEGER,
            supplier TEXT,
            last_updated TEXT,
            warranty_period TEXT
        )
        """)
        
        # Insert sample data
        insert_sample_data(cursor)
        
        conn.commit()
        logger.info("Database created and populated successfully")
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
    finally:
        conn.close()

def insert_sample_data(cursor):
    """Insert sample data into all tables"""
    
    # Customers data
    customers = [
        ('C001', 'Dennis Kimaita', 'dkimaita22@gmail.com', '+254769375587', 
         '2024-01-15', 5, 500.50, 'Premium'),
        ('C002', 'Jane Smith', 'kimaitaduzit@gmail.com', '+254746493184', 
         '2024-02-20', 3, 299.99, 'Regular'),
        ('C003', 'Bob Johnson', 'devtest@ngkkenya.com', '+254706397373', 
         '2024-03-10', 8, 850.00, 'Premium')
    ]
    
    cursor.executemany("""
    INSERT INTO customers 
    (customer_id, name, email, phone, registration_date, total_orders, total_spent, customer_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)
    
    # Agents data
    agents = [
        ('A001', 'Sarah Connor', 'sarah@company.com', 'Sales', 
         '2023-01-10', 10000, 12500, 4.5, 'North'),
        ('A002', 'Mike Ross', 'mike@company.com', 'Support', 
         '2023-03-15', 8000, 7500, 4.2, 'South'),
        ('A003', 'Rachel Green', 'rachel@company.com', 'Marketing', 
         '2023-05-20', 12000, 13200, 4.8, 'East'),
        ('A004', 'Harvey Specter', 'harvey@company.com', 'Sales', 
         '2023-02-28', 15000, 16800, 4.9, 'West')
    ]
    
    cursor.executemany("""
    INSERT INTO agents 
    (agent_id, name, email, department, hire_date, sales_target, sales_achieved, performance_rating, region)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, agents)
    
    # Inventory data
    inventory = [
        ('P001', 'Laptop Pro', 'Electronics', 1299.99, 800.00, 
         25, 10, 'TechCorp', '2024-07-01', '1 Year'),
        ('P002', 'Wireless Mouse', 'Accessories', 79.99, 35.50, 
         150, 50, 'AccessoryPlus', '2024-07-02', '1 Year'),
        ('P003', 'Keyboard Mechanical', 'Accessories', 149.99, 75.00, 
         75, 25, 'KeyboardKing', '2024-07-01', '2 Years'),
        ('P004', 'Monitor 24"', 'Electronics', 299.99, 180.00, 
         40, 15, 'DisplayMax', '2024-07-03', '1 Year'),
        ('P005', 'Headphones', 'Accessories', 199.99, 90.00, 
         90, 30, 'AudioTech', '2024-07-02', '1 Year')
    ]
    
    cursor.executemany("""
    INSERT INTO inventory 
    (product_id, product_name, category, price, cost, stock_quantity, reorder_level, supplier, last_updated, warranty_period)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, inventory)
    
    logger.info(f"Inserted {len(customers)} customers, {len(agents)} agents, and {len(inventory)} inventory items")

def verify_data(db_name='business_automation.db'):
    """Verify the inserted data"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        logger.info("\nVerifying database content:")
        
        # Count records in each table
        for table in ['customers', 'agents', 'inventory']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"{table.capitalize()}: {count} records")
        
        # Show sample records
        cursor.execute("SELECT * FROM customers LIMIT 1")
        logger.info("\nSample customer:\n" + str(cursor.fetchone()))
        
        cursor.execute("SELECT * FROM agents LIMIT 1")
        logger.info("\nSample agent:\n" + str(cursor.fetchone()))
        
        cursor.execute("SELECT * FROM inventory LIMIT 1")
        logger.info("\nSample inventory item:\n" + str(cursor.fetchone()))
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
    verify_data()
    logger.info("Database setup complete!")