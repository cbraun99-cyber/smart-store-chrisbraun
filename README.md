# Pro Analytics 02 Python Starter Repository

> Use this repo to start a professional Python project.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![UV](https://img.shields.io/badge/package_manager-uv-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-blue.svg)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd pro-analytics-02-python-starter
uv venv
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install

# Process data and build warehouse
uv run python src/analytics_project/data_prep.py
uv run python src/analytics_project/etl_to_dw.py
```

## ✨ Features

**Core Capabilities:**
- 🏗️ **Environment Management**: UV, Virtual Environments
- ✅ **Code Quality**: Ruff, pre-commit, pytest
- 📚 **Documentation**: MkDocs, GitHub Pages
- 📊 **Data Processing**: Pandas, Data Validation
- 🗃️ **Data Warehouse**: SQLite, Star Schema
- 🔄 **CI/CD**: GitHub Actions

**Professional Skills Development:**
- **Environment Management**: Every project in isolation
- **Code Quality**: Automated checks for fewer bugs
- **Documentation**: Use modern project documentation tools
- **Testing**: Prove your code works
- **Version Control**: Collaborate professionally

---

## 📋 Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- Git
- VS Code (recommended)

## 📚 Documentation

- [Project Structure](./STRUCTURE.md)
- [Machine Setup](./SET_UP_MACHINE.md)
- [Project Setup](./SET_UP_PROJECT.md)
- Additional information: <https://github.com/denisecase/pro-analytics-02>

---

## 🔧 WORKFLOW 1. Set Up Your Machine

Proper setup is critical.
Complete each step in the following guide and verify carefully.

- [SET UP MACHINE](./SET_UP_MACHINE.md)

---

## 🛠️ WORKFLOW 2. Set Up Your Project

After verifying your machine is set up, set up a new Python project by copying this template.
Complete each step in the following guide.

- [SET UP PROJECT](./SET_UP_PROJECT.md)

It includes the critical commands to set up your local environment (and activate it):

```bash
uv venv
uv python pin 3.12
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
uv run python --version
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\activate
```

**macOS / Linux / WSL:**
```bash
source .venv/bin/activate
```

---

## 📊 WORKFLOW 3. Daily Workflow

Please ensure that the prior steps have been verified before continuing.
When working on a project, we open just that project in VS Code.

### 3.1 Git Pull from GitHub

Always start with `git pull` to check for any changes made to the GitHub repo.

```bash
git pull
```

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

```bash
uv sync --extra dev --extra docs --upgrade
uv cache clean
git add .
uvx ruff check --fix
uvx pre-commit autoupdate
uv run pre-commit run --all-files
git add .
uv run pytest
```

NOTE: The second `git add .` ensures any automatic fixes made by Ruff or pre-commit are included before testing or committing.

*Note on best practices:*
`uvx` runs the latest version of a tool in an isolated cache, outside the virtual environment.
This keeps the project light and simple, but behavior can change when the tool updates.
For fully reproducible results, or when you need to use the local `.venv`, use `uv run` instead.

### 3.3 Build Project Documentation

Make sure you have current doc dependencies, then build your docs, fix any errors, and serve them locally to test.

```bash
uv run mkdocs build --strict
uv run mkdocs serve
```

- After running the serve command, the local URL of the docs will be provided. To open the site, press **CTRL and click** the provided link (at the same time) to view the documentation. On a Mac, use **CMD and click**.
- Press **CTRL c** (at the same time) to stop the hosting process.

### 3.4 Execute Demo Modules

This project includes demo code.
Run the demo Python modules to confirm everything is working.

In VS Code terminal, run:

```bash
uv run python -m analytics_project.demo_module_basics
uv run python -m analytics_project.demo_module_languages
uv run python -m analytics_project.demo_module_stats
uv run python -m analytics_project.demo_module_viz
```

You should see:

- Log messages in the terminal
- Greetings in several languages
- Simple statistics
- A chart window open (close the chart window to continue).

### 3.5 Execute Data Processing Pipeline

You have two options for processing your data - individual scripts or a unified pipeline:

## 🚀 Execution Options

### Option A: Unified Data Preparation (Recommended for Production)
```bash
uv run python src/analytics_project/data_prep.py
```

**Benefits:**
- Single command processes all datasets
- Consistent logging and error handling
- Cross-dataset validation
- Better for automated workflows

### Option B: Individual Data Preparation Scripts (Recommended for Development/Debugging)
Run the individual data preparation scripts to process CSV files and created cleaned datasets:

##### Customer Data Preparation
```bash
uv run python scripts/data_preparation/prepare_customers_data.py
```

**Benefits:**
- Isolated processing for debugging
- Detailed logs for each dataset
- Easier to identify dataset-specific issues

##### Product Data Preparation
```bash
uv run python scripts/data_preparation/prepare_products_data.py
```

##### Sales Data Preparation
```bash
uv run python scripts/data_preparation/prepare_sales_data.py
```

**Expected Output for All Scripts:**
- Detailed log messages showing each processing step
- DataFrame shapes before and after cleaning
- Validation reports and data quality metrics
- Cleaned CSV files saved to `data/prepared/` directory

### 3.6 Execute Data Warehouse ETL Pipeline

After preparing your data, build the data warehouse using the ETL script:

```bash
uv run python src/analytics_project/etl_to_dw.py
```

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

```bash
git add .
git commit -m "describe your change in quotes"
git push -u origin main
```

This will trigger the GitHub Actions workflow and publish your documentation via GitHub Pages.

### 3.8 Modify and Debug

With a working version safe in GitHub, start making changes to the code.

Before starting a new session, remember to do a `git pull` and keep your tools updated.

Each time forward progress is made, remember to git add-commit-push.

### 3.9 Data Development Workflow

**When modifying data processing:**
1. Make changes to individual preparation scripts for testing
2. Run the specific script to verify changes
3. Once working, integrate changes into the unified `data_prep.py`
4. Test the unified pipeline end-to-end
5. Update documentation if new columns or validation rules are added

**Adding New Data Sources:**
1. Create new preparation script in `scripts/data_preparation/`
2. Follow existing patterns in `DataScrubber` class
3. Add to unified pipeline in `data_prep.py`
4. Update data warehouse schema in `etl_to_dw.py`
5. Update validation in `validate_data_integrity()`

---

## 🔍 Data Quality & Validation

**Comprehensive Data Validation:**
- **DataScrubber Class**: Reusable utility for consistent data cleaning across all datasets
- **Statistical Outlier Detection**: IQR method for identifying and removing outliers
- **Business Rule Validation**: Enforces domain-specific rules (discount percentages 0-100%, valid payment types, etc.)
- **Cross-Dataset Integrity**: Validates relationships between customers, products, and sales
- **Data Profiling**: Automatic logging of data shapes, types, and quality metrics

**Validation Checks:**
- CustomerID and ProductID uniqueness
- Referential integrity between sales and dimension tables
- Numeric range validation (loyalty points, stock quantities, sale amounts)
- Categorical value standardization
- Date format consistency

---

## 📁 Data Requirements

### Expected Input File Structure

**Required CSV files in `data/raw/`:**
- `customers_data.csv` - Must contain: CustomerID, Name, Region, JoinDate
- `products_data.csv` - Must contain: ProductID, ProductName, Category, UnitPrice, Supplier
- `sales_data.csv` - Must contain: TransactionID, SaleDate, CustomerID, ProductID, SaleAmount

**Optional Columns (will be generated if missing):**
- Customers: LoyaltyPoints, CustomerSegment
- Products: StockQuantity, ProductCategory
- Sales: DiscountPercent, PaymentType, CampaignID, StoreID

### Data Quality Expectations
- Files should be UTF-8 encoded CSV
- Primary keys (CustomerID, ProductID, TransactionID) must be unique
- Dates should be in recognizable formats
- Numeric columns should contain valid numbers

---

## 🗃️ Data Warehouse Implementation

### Design Decisions

**Schema Type**: Star Schema
**Rationale**: Simplest and most efficient for analytical queries, minimizes join complexity
**Fact Table**: `sales` - contains transactional business metrics
**Dimension Tables**: `customers`, `products` - provide descriptive context

**Key Design Principles:**
- Denormalized structure for query performance
- Clear primary and foreign key relationships
- Business-focused column selection

### Schema Definition

**Customers Dimension Table:**
- customerid (TEXT, Primary Key)
- name (TEXT)
- region (TEXT)
- joindate (TEXT)
- loyaltypoints (REAL)
- customertier (TEXT)
- customersegment (TEXT)

**Products Dimension Table:**
- productid (TEXT, Primary Key)
- productname (TEXT)
- category (TEXT)
- unitprice (REAL)
- stockquantity (INTEGER)
- supplier (TEXT)
- productcategory (TEXT)

**Sales Fact Table:**
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

**Data Sources:**
- `data/prepared/customers_prepared.csv`
- `data/prepared/products_prepared.csv`
- `data/prepared/sales_prepared.csv`

### Business Value

**Customer Analytics:**
- Customer segmentation by region and loyalty
- Customer lifetime value analysis
- Regional sales performance

**Product Analytics:**
- Sales performance by product category
- Pricing and discount strategy analysis
- Supplier performance tracking

**Sales Analytics:**
- Campaign effectiveness measurement
- Payment method preferences
- Seasonal sales trends

---

## ✨ Key Technical Features

**Modular Architecture:**
- **DataScrubber**: Reusable cleaning utility with consistent API
- **Unified Pipeline**: Single entry point for all data processing
- **Individual Scripts**: Isolated processing for development/debugging

**Production-Ready:**
- Comprehensive logging at every step
- Robust error handling and validation
- Data quality metrics and reporting
- Cross-dataset integrity checks

**Extensible Design:**
- Easy to add new data sources
- Configurable cleaning rules
- Modular validation framework

---

## 🔄 Data Processing Features

### Reusable DataScrubber Class
- **Modular Design**: Encapsulates common data cleaning operations in a reusable class
- **Consistent API**: Standardized methods for column cleaning, duplicate removal, missing value handling
- **Extensible**: Easy to add new cleaning methods for specific business needs
- **Validation**: Built-in data validation against configurable business rules

### Customer Data Processing
- **Column Addition**: Adds LoyaltyPoints and CustomerSegment columns with realistic distributions
- **Data Cleaning**: Handles missing values, removes duplicates, and standardizes segment names
- **Validation**: Ensures CustomerID uniqueness and valid loyalty point ranges
- **Outlier Removal**: Filters extreme loyalty points and invalid customer IDs

### Product Data Processing
- **Column Addition**: Adds StockQuantity and ProductCategory columns with realistic values
- **Data Cleaning**: Standardizes category names, handles negative stock quantities
- **Quality Control**: Uses IQR method for outlier detection in stock levels
- **Format Standardization**: Converts text to title case and ensures proper data types

### Sales Data Processing
- **Numeric Cleaning**: Converts all numeric columns to proper types, handles conversion errors
- **Date Standardization**: Converts SaleDate to consistent YYYY-MM-DD format
- **Business Logic**: Validates discount percentages (0-100%) and payment types
- **Outlier Detection**: Removes negative sales and extreme sale amounts using statistical methods
- **Data Integrity**: Cross-references customers and products to identify orphaned records

---

## ❓ Enhanced Troubleshooting

### Common Issues

**Pre-commit hooks failing:**
```bash
uv run pre-commit run --all-files
```

**Module not found errors:**
```bash
uv sync --extra dev --extra docs --upgrade
```

**Data file path issues:**
- Ensure you're running commands from project root
- Verify CSV files are in `data/raw/` with exact names

### Data Preparation Issues

**Missing Columns:**
- Scripts automatically generate missing optional columns with realistic data
- Required columns will cause failures if missing

**Data Type Conversion Errors:**
- Check for non-numeric values in numeric columns
- Verify date formats are consistent

**Foreign Key Violations:**
- Run individual preparation scripts to identify orphaned records
- Check logs for cross-dataset validation warnings

### Performance Tips

**Large Datasets:**
- Use unified pipeline for better performance
- Monitor memory usage with very large files
- Consider chunk processing for datasets > 1GB

**Debugging:**
- Run individual scripts for detailed dataset-specific logging
- Check `utils/logger.py` for log configuration options
- Use `uv run python -m pdb script.py` for interactive debugging

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

---

## 🗺️ Development Roadmap

- [ ] Add more data validation rules
- [ ] Implement data quality metrics dashboard
- [ ] Add automated data profiling
- [ ] Support for additional database backends

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🔄 Data Flow

Raw CSV Files → Data Preparation → Cleaned Data → ETL Process → Data Warehouse → Analytics

---

## 📁 File Structure

```
src/analytics_project/
├── etl_to_dw.py              # Data warehouse ETL pipeline
├── data_prep.py              # Unified data preparation orchestrator
├── demo_module_*.py          # Demo modules
└── utils_logger.py           # Logging utilities

scripts/data_preparation/
├── prepare_customers_data.py # Individual customer data preparation
├── prepare_products_data.py  # Individual product data preparation
└── prepare_sales_data.py     # Individual sales data preparation

utils/
├── logger.py                 # Logger configuration
└── data_scrubber.py          # Reusable DataScrubber class

data/
├── dw/                       # Data warehouse database (output)
├── prepared/                 # Cleaned CSV files (output)
└── raw/                      # Raw CSV files (input)
```

---

*Last updated: November 11, 2025*
