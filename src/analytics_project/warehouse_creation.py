import duckdb
import pandas as pd

# Create or connect to DuckDB database
conn = duckdb.connect('my_data_warehouse.duckdb')

print("Building Data Warehouse...")

# Create tables with optimized schema
conn.execute("""
    -- Create customers dimension table
    CREATE OR REPLACE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        region TEXT,
        join_date TEXT,
        loyalty_points REAL,
        customer_tier TEXT,
        customer_segment TEXT
    );

    -- Create products dimension table
    CREATE OR REPLACE TABLE products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        unit_price REAL,
        stock_quantity INTEGER,
        supplier TEXT,
        product_category TEXT
    );

    -- Create sales fact table
    CREATE OR REPLACE TABLE sales (
        transaction_id INTEGER PRIMARY KEY,
        sale_date TEXT,
        customer_id TEXT,
        product_id TEXT,
        store_id TEXT,
        campaign_id TEXT,
        sale_amount REAL,
        discount_percent REAL,
        payment_type TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
""")

print("Tables created successfully!")

# Load data from CSV files
print("Loading data...")

# Load customers data with data cleaning
conn.execute("""
    INSERT OR REPLACE INTO customers
    SELECT
        customerid,
        name,
        UPPER(TRIM(region)) as region,  -- Clean region data
        joindate,
        loyaltypoints,
        COALESCE(NULLIF(customertier, ''), 'Unknown') as customer_tier,  -- Handle missing tiers
        customersegment
    FROM read_csv('customers_prepared.csv', auto_detect=true)
""")

# Load products data
conn.execute("""
    INSERT OR REPLACE INTO products
    SELECT * FROM read_csv('products_prepared.csv', auto_detect=true)
""")

# Load sales data with data cleaning and date formatting
conn.execute("""
    INSERT OR REPLACE INTO sales
    SELECT
        transactionid,
        strptime(saledate, '%m/%d/%Y')::date as sale_date,  -- Convert to proper date
        customerid,
        productid,
        storeid,
        COALESCE(NULLIF(campaignid, ''), '0') as campaign_id,  -- Handle missing campaign IDs
        COALESCE(saleamount, 0) as sale_amount,  -- Handle missing sale amounts
        discountpercent,
        COALESCE(NULLIF(paymenttype, ''), 'Unknown') as payment_type  -- Handle missing payment types
    FROM read_csv('sales_prepared.csv', auto_detect=true)
""")

print("Data loaded successfully!")

# Verify the data warehouse
print("\n=== Data Warehouse Verification ===")

# Check row counts
tables = ['customers', 'products', 'sales']
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")

# Sample query to test the star schema
print("\n=== Sample Analytical Query ===")
result = conn.execute("""
    SELECT
        c.region,
        p.category,
        SUM(s.sale_amount) as total_sales,
        COUNT(*) as transaction_count,
        AVG(s.discount_percent) as avg_discount
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    JOIN products p ON s.product_id = p.product_id
    GROUP BY c.region, p.category
    ORDER BY total_sales DESC
    LIMIT 10
""").df()

print(result)

# Close connection
conn.close()

print("\nData warehouse built successfully! Ready for analysis.")
