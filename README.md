# Building #this is the modified from web version#
Bootcamp Exercise

## Data Pipeline

This project contains a Python script that performs a simple ETL (Extract, Transform, Load) process on a sales dataset.

### Prerequisites

- Python 3
- A virtual environment (recommended)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline

To run the data pipeline, execute the following command:

```bash
python data_pipeline.py
```

This will:

- Read the `sales_data.csv` file.
- Clean the data.
- Generate insights on the top 10 products by revenue.
- Create a `top_10_products.png` visualization.
- Store the cleaned data in a `sales.db` SQLite database.
- Log the entire process in `pipeline.log`.
