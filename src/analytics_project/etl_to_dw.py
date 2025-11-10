import pandas as pd
import sqlite3
import pathlib
import sys

# For local imports, temporarily add project root to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Constants
DW_DIR = pathlib.Path("data").joinpath("dw")
DB_PATH = DW_DIR.joinpath("smart_sales.db")
PREPARED_DATA_DIR = pathlib.Path("data").joinpath("prepared")


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create tables in the data warehouse if they don't exist."""
    # Customers dimension table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customerid TEXT PRIMARY KEY,
            name TEXT,
            region TEXT,
            joindate TEXT,
            loyaltypoints REAL,
            customertier TEXT,
            customersegment TEXT
        )
    """)

    # Products dimension table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            productid TEXT PRIMARY KEY,
            productname TEXT,
            category TEXT,
            unitprice REAL,
            stockquantity INTEGER,
            supplier TEXT,
            productcategory TEXT
        )
    """)

    # Sales fact table
    cursor.execute("""
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
            FOREIGN KEY (customerid) REFERENCES customers (customerid),
            FOREIGN KEY (productid) REFERENCES products (productid)
        )
    """)


def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from the customers, products, and sales tables."""
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM products")


def clean_customers_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize customers data."""
    df = df.copy()
    df['region'] = df['region'].str.upper().str.strip()
    df['customertier'] = df['customertier'].fillna('Unknown')
    return df


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize sales data."""
    df = df.copy()
    # Handle missing values
    df['campaignid'] = df['campaignid'].fillna('0')
    df['saleamount'] = df['saleamount'].fillna(0)
    df['paymenttype'] = df['paymenttype'].fillna('Unknown')
    return df


def insert_customers(customers_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert customer data into the customers table."""
    customers_df = clean_customers_data(customers_df)
    customers_df.to_sql("customers", cursor.connection, if_exists="append", index=False)


def insert_products(products_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert product data into the products table."""
    products_df.to_sql("products", cursor.connection, if_exists="append", index=False)


def insert_sales(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert sales data into the sales table."""
    sales_df = clean_sales_data(sales_df)
    sales_df.to_sql("sales", cursor.connection, if_exists="append", index=False)


def load_data_to_db() -> None:
    """Main function to load data into the data warehouse."""
    conn = None
    try:
        # Create data warehouse directory if it doesn't exist
        DW_DIR.mkdir(parents=True, exist_ok=True)

        # Connect to SQLite – will create the file if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Creating data warehouse schema...")
        create_schema(cursor)

        print("Clearing existing records...")
        delete_existing_records(cursor)

        print("Loading prepared data...")
        # Load prepared data using pandas
        customers_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("customers_prepared.csv"))
        products_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("products_prepared.csv"))
        sales_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("sales_prepared.csv"))

        print("Inserting data into database...")
        # Insert data into the database
        insert_customers(customers_df, cursor)
        insert_products(products_df, cursor)
        insert_sales(sales_df, cursor)

        conn.commit()
        print("Data warehouse populated successfully!")

        # Verify data was loaded
        for table in ['customers', 'products', 'sales']:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count} rows")

    except Exception as e:
        print(f"Error loading data: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    load_data_to_db()
