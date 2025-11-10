# Pro Analytics 02 Python Starter Repository

> Use this repo to start a professional Python project.

- Additional information: <https://github.com/denisecase/pro-analytics-02>
- Project organization: [STRUCTURE](./STRUCTURE.md)
- Build professional skills:
  - **Environment Management**: Every project in isolation
  - **Code Quality**: Automated checks for fewer bugs
  - **Documentation**: Use modern project documentation tools
  - **Testing**: Prove your code works
  - **Version Control**: Collaborate professionally

---

## WORKFLOW 1. Set Up Your Machine

Proper setup is critical.
Complete each step in the following guide and verify carefully.

- [SET UP MACHINE](./SET_UP_MACHINE.md)

---

## WORKFLOW 2. Set Up Your Project

After verifying your machine is set up, set up a new Python project by copying this template.
Complete each step in the following guide.

- [SET UP PROJECT](./SET_UP_PROJECT.md)

It includes the critical commands to set up your local environment (and activate it):

`uv venv`
`uv python pin 3.12`
`uv sync --extra dev --extra docs --upgrade`
`uv run pre-commit install`
`uv run python --version`

**Windows (PowerShell):**
`.\.venv\Scripts\activate`

**macOS / Linux / WSL:**
`source .venv/bin/activate`

---

## WORKFLOW 3. Daily Workflow

Please ensure that the prior steps have been verified before continuing.
When working on a project, we open just that project in VS Code.

### 3.1 Git Pull from GitHub

Always start with `git pull` to check for any changes made to the GitHub repo.

`git pull`

### 3.2 Run Checks as You Work

This mirrors real work where we typically:

1. Update dependencies (for security and compatibility).
2. Clean unused cached packages to free space.
3. Use `git add .` to stage all changes.
4. Run ruff and fix minor issues.
5. Update pre-commit periodically.
6. Run pre-commit quality checks on all code files (**twice if needed**, the first pass may fix things).
7. Run tests.

In VS Code, open your repository, then open a terminal (Terminal / New Terminal) and run the following commands one at a time to check the code.

`uv sync --extra dev --extra docs --upgrade`
`uv cache clean`
`git add .`
`uvx ruff check --fix`
`uvx pre-commit autoupdate`
`uv run pre-commit run --all-files`
`git add .`
`uv run pytest`

NOTE: The second `git add .` ensures any automatic fixes made by Ruff or pre-commit are included before testing or committing.

*Note on best practices:*
`uvx` runs the latest version of a tool in an isolated cache, outside the virtual environment.
This keeps the project light and simple, but behavior can change when the tool updates.
For fully reproducible results, or when you need to use the local `.venv`, use `uv run` instead.

### 3.3 Build Project Documentation

Make sure you have current doc dependencies, then build your docs, fix any errors, and serve them locally to test.

`uv run mkdocs build --strict`
`uv run mkdocs serve`

- After running the serve command, the local URL of the docs will be provided. To open the site, press **CTRL and click** the provided link (at the same time) to view the documentation. On a Mac, use **CMD and click**.
- Press **CTRL c** (at the same time) to stop the hosting process.

### 3.4 Execute Demo Modules

This project includes demo code.
Run the demo Python modules to confirm everything is working.

In VS Code terminal, run:

`uv run python -m analytics_project.demo_module_basics`
`uv run python -m analytics_project.demo_module_languages`
`uv run python -m analytics_project.demo_module_stats`
`uv run python -m analytics_project.demo_module_viz`

You should see:

- Log messages in the terminal
- Greetings in several languages
- Simple statistics
- A chart window open (close the chart window to continue).

### 3.5 Execute Data Processing Pipeline

You have two options for processing your data - individual scripts or a unified pipeline:

#### Option A: Unified Data Preparation (Recommended)
`uv run python src/analytics_project/data_prep.py`

**Features:**
- Processes all 3 datasets in a single execution
- Uses reusable `DataScrubber` class for consistent cleaning
- Applies dataset-specific business logic and validation
- Performs cross-dataset integrity checks
- Provides comprehensive logging and summary reporting

#### Option B: Individual Data Preparation Scripts
Run the individual data preparation scripts to process CSV files and create cleaned datasets:

##### Customer Data Preparation
`uv run python scripts/data_preparation/prepare_customers_data.py`

**Features:**
- Adds customer-related columns (LoyaltyPoints, CustomerSegment)
- Removes duplicate customers based on CustomerID
- Handles missing values (fills LoyaltyPoints with 0, CustomerSegment with 'Unknown')
- Cleans and validates loyalty points and customer segments
- Removes outliers and invalid CustomerIDs

##### Product Data Preparation
`uv run python scripts/data_preparation/prepare_products_data.py`

**Features:**
- Adds product-related columns (StockQuantity, ProductCategory)
- Removes duplicate products based on ProductID
- Handles missing values (fills StockQuantity with 0, ProductCategory with 'Uncategorized')
- Cleans stock quantities and standardizes product categories
- Removes outliers using IQR method
- Standardizes text formatting

##### Sales Data Preparation
`uv run python scripts/data_preparation/prepare_sales_data.py`

**Features:**
- Cleans numeric columns (SaleAmount, DiscountPercent, etc.)
- Standardizes date formats and removes invalid dates
- Removes duplicate transactions based on TransactionID
- Handles missing values (fills CampaignID with -1, DiscountPercent with 0)
- Cleans discount percentages and payment types
- Removes outliers based on sale amounts

**Expected Output for All Scripts:**
- Detailed log messages showing each processing step
- DataFrame shapes before and after cleaning
- Validation reports and data quality metrics
- Cleaned CSV files saved to `data/prepared/` directory

### 3.6 Execute Data Warehouse ETL Pipeline

After preparing your data, build the data warehouse using the ETL script:

`uv run python src/analytics_project/etl_to_dw.py`

**Features:**
- Creates star schema data warehouse in SQLite
- Loads cleaned data from `data/prepared/` directory
- Establishes foreign key relationships between tables
- Performs data validation and quality checks
- Outputs verification statistics

### 3.7 Git add-commit-push to GitHub

Anytime we make working changes to code is a good time to git add-commit-push to GitHub.

1. Stage your changes with git add.
2. Commit your changes with a useful message in quotes.
3. Push your work to GitHub.

`git add .`
`git commit -m "describe your change in quotes"`
`git push -u origin main`

This will trigger the GitHub Actions workflow and publish your documentation via GitHub Pages.

### 3.8 Modify and Debug

With a working version safe in GitHub, start making changes to the code.

Before starting a new session, remember to do a `git pull` and keep your tools updated.

Each time forward progress is made, remember to git add-commit-push.

---

## Data Warehouse Implementation (P4)

### Design Decisions

**Schema Type**: Star Schema
**Rationale**: Simplest and most efficient for analytical queries, minimizes join complexity
**Fact Table**: `sales` - contains transactional business metrics
**Dimension Tables**: `customers`, `products` - provide descriptive context

**Key Design Principles**:
- Denormalized structure for query performance
- Clear primary and foreign key relationships
- Business-focused column selection

### Schema Definition

**Customers Dimension Table**:
- customerid (TEXT, Primary Key)
- name (TEXT)
- region (TEXT)
- joindate (TEXT)
- loyaltypoints (REAL)
- customertier (TEXT)
- customersegment (TEXT)

**Products Dimension Table**:
- productid (TEXT, Primary Key)
- productname (TEXT)
- category (TEXT)
- unitprice (REAL)
- stockquantity (INTEGER)
- supplier (TEXT)
- productcategory (TEXT)

**Sales Fact Table**:
- transactionid (INTEGER, Primary Key)
- saledate (TEXT)
- customerid (TEXT, Foreign Key)
- productid (TEXT, Foreign Key)
- storeid (TEXT)
- campaignid (TEXT)
- saleamount (REAL)
- discountpercent (REAL)
- paymenttype (TEXT)

### Implementation Details

**ETL Script**: `src/analytics_project/etl_to_dw.py`
- Creates database schema
- Loads data from prepared CSV files
- Establishes referential integrity
- Performs data validation

**Database Location**: `data/dw/smart_sales.db`

**Data Sources**:
- `data/prepared/customers_prepared.csv`
- `data/prepared/products_prepared.csv`
- `data/prepared/sales_prepared.csv`

### Business Value

**Customer Analytics**:
- Customer segmentation by region and loyalty
- Customer lifetime value analysis
- Regional sales performance

**Product Analytics**:
- Sales performance by product category
- Pricing and discount strategy analysis
- Supplier performance tracking

**Sales Analytics**:
- Campaign effectiveness measurement
- Payment method preferences
- Seasonal sales trends

### Challenges & Solutions

1. **Data Type Compatibility**: Used TEXT for dates and proper REAL/INTEGER types for numeric data in SQLite
2. **Column Naming**: Maintained camelCase from prepared data files for consistency
3. **Date Formatting**: Converted to ISO 8601 format (YYYY-MM-DD) for proper sorting
4. **Missing Values**: Implemented robust handling for null values in campaign IDs and payment types
5. **Data Integrity**: Established foreign key constraints between fact and dimension tables

### Project Structure

The data warehouse integrates with the existing project structure:

- **data/dw/**: Contains the SQLite database file
- **data/prepared/**: Source CSV files for ETL process
- **src/analytics_project/etl_to_dw.py**: Main ETL script
- **src/analytics_project/data_prep.py**: Data preparation script

### Usage Examples

**Sample Analytical Queries**:

- **Sales by region and product category**: Analyze total sales across different regions and product categories
- **Customer loyalty analysis**: Examine average loyalty points by customer tier and segment
- **Campaign performance**: Measure sales impact of different marketing campaigns
- **Product performance**: Track sales by product category and supplier

### Execution Commands

1. Prepare data: `uv run python src/analytics_project/data_prep.py`
2. Build warehouse: `uv run python src/analytics_project/etl_to_dw.py`

---

## Data Files Preparation

For the data processing pipeline to work, ensure your CSV files are placed in the correct location:

1. Create the data directory structure:
   `mkdir -p data/raw data/prepared data/dw`

2. Place your CSV files in `data/raw/` with these expected names:
   - `customers_data.csv`
   - `products_data.csv`
   - `sales_data.csv`

3. Run the data preparation using either approach:
   - **Unified**: `uv run python src/analytics_project/data_prep.py`
   - **Individual**: Run each script separately as shown above

4. Build the data warehouse:
   `uv run python src/analytics_project/etl_to_dw.py`

## Troubleshooting

If any data preparation script fails, check:

- Are you in the root project folder when running commands?
- Do the CSV files exist in `data/raw/` with correct names?
- Are there any error messages in the terminal or log files?
- Did you run `uv sync` to ensure all dependencies are installed?
- Check individual script logs for specific data quality issues

If the ETL script fails, verify:

- Are the prepared CSV files in `data/prepared/` directory?
- Is the data warehouse directory structure created?
- Are there any foreign key constraint violations?
- Check the verification output for data loading issues

View detailed logs for each script execution to identify and resolve data quality problems.
