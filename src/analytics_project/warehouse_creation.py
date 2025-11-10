import sqlite3
import pandas as pd
from datetime import datetime

# Create or connect to SQLite database
conn = sqlite3.connect('my_data_warehouse.db')
cursor = conn.cursor()

print("Building Data Warehouse with SQLite...")

# Create tables with optimized schema - using EXACT column names from CSV
cursor.execute("""
    -- Create customers dimension table
    CREATE TABLE IF NOT EXISTS customers (
        customerid TEXT PRIMARY KEY,
        name TEXT,
        region TEXT,
        joindate TEXT,
        loyaltypoints REAL,
        customertier TEXT,
        customersegment TEXT
    );
""")

cursor.execute("""
    -- Create products dimension table
    CREATE TABLE IF NOT EXISTS products (
        productid TEXT PRIMARY KEY,
        productname TEXT,
        category TEXT,
        unitprice REAL,
        stockquantity INTEGER,
        supplier TEXT,
        productcategory TEXT
    );
""")

cursor.execute("""
    -- Create sales fact table
    CREATE TABLE IF NOT EXISTS sales (
        transactionid INTEGER PRIMARY KEY,
        saledate TEXT,
        customerid TEXT,
        productid TEXT,
        storeid TEXT,
        campaignid TEXT,
        saleamount REAL,
        discountpercent REAL,
        paymenttype TEXT,
        FOREIGN KEY (customerid) REFERENCES customers(customerid),
        FOREIGN KEY (productid) REFERENCES products(productid)
    );
""")

print("Tables created successfully!")

# Load data from CSV files with correct paths
print("Loading data...")

# Load customers data from data/prepared/ directory
customers_df = pd.read_csv('data/prepared/customers_prepared.csv')
# Clean and standardize the data
customers_df['region'] = customers_df['region'].str.upper().str.strip()
customers_df['customertier'] = customers_df['customertier'].fillna('Unknown')
customers_df.to_sql('customers', conn, if_exists='replace', index=False)

# Load products data
products_df = pd.read_csv('data/prepared/products_prepared.csv')
products_df.to_sql('products', conn, if_exists='replace', index=False)

# Load and clean sales data
sales_df = pd.read_csv('data/prepared/sales_prepared.csv')


# Convert date format from MM/DD/YYYY to YYYY-MM-DD (ISO 8601)
def convert_date(date_str):
    try:
        return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
    except:
        return date_str


sales_df['saledate'] = sales_df['saledate'].apply(convert_date)
# Handle missing values
sales_df['campaignid'] = sales_df['campaignid'].fillna('0')
sales_df['saleamount'] = sales_df['saleamount'].fillna(0)
sales_df['paymenttype'] = sales_df['paymenttype'].fillna('Unknown')

sales_df.to_sql('sales', conn, if_exists='replace', index=False)

print("Data loaded successfully!")

# Verify the data warehouse
print("\n=== Data Warehouse Verification ===")

# Check row counts
tables = ['customers', 'products', 'sales']
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")

# Verify column names in each table
print("\n=== Column Names Verification ===")
for table in tables:
    columns = cursor.execute(f"PRAGMA table_info({table})").fetchall()
    print(f"{table} columns: {[col[1] for col in columns]}")

# Sample query to test the star schema - using ACTUAL column names
print("\n=== Sample Analytical Query ===")
result = pd.read_sql_query(
    """
    SELECT
        c.region,
        p.category,
        SUM(s.saleamount) as total_sales,
        COUNT(*) as transaction_count,
        AVG(s.discountpercent) as avg_discount
    FROM sales s
    JOIN customers c ON s.customerid = c.customerid
    JOIN products p ON s.productid = p.productid
    GROUP BY c.region, p.category
    ORDER BY total_sales DESC
    LIMIT 10
""",
    conn,
)

print(result)

# Close connection
conn.close()

print("\nData warehouse built successfully with SQLite! Ready for analysis.")
