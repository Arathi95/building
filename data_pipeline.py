import pandas as pd
import matplotlib.pyplot as plt
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(filename='pipeline.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def read_csv_in_chunks(file_path, chunk_size=10000):
    """Reads a CSV file in chunks and returns an iterator."""
    logging.info(f"Reading data from {file_path} in chunks of {chunk_size}...")
    try:
        return pd.read_csv(file_path, chunksize=chunk_size)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None

def clean_data(df):
    """Cleans the DataFrame by handling missing values."""
    logging.info("Cleaning a chunk of data...")
    # Drop rows with missing 'date'
    df.dropna(subset=['date'], inplace=True)
    # Fill missing 'quantity' and 'revenue' with 0
    df.fillna({'quantity': 0, 'revenue': 0}, inplace=True)
    logging.info("Chunk cleaning complete.")
    return df

def create_visualisation(insights, output_path):
    """Creates a bar chart visualisation of the insights."""
    logging.info("Creating visualisation...")
    plt.figure(figsize=(10, 6))
    insights.plot(kind='bar')
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Product ID')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    logging.info(f"Visualisation saved to {output_path}")
    plt.close()

def main():
    """Main function to run the data pipeline."""
    logging.info("Starting data pipeline...")
    
    # --- Configuration ---
    CSV_FILE = 'sales_data.csv'
    DB_FILE = 'sales.db'
    VISUALISATION_FILE = 'top_10_products.png'
    CHUNK_SIZE = 10000  # Adjust chunk size based on available memory and file size

    # --- ETL Process ---
    chunk_iterator = read_csv_in_chunks(CSV_FILE, CHUNK_SIZE)
    
    if chunk_iterator is not None:
        engine = create_engine(f'sqlite:///{DB_FILE}')
        total_revenue_per_product = pd.Series(dtype='float64')
        
        # Truncate the table before starting
        with engine.connect() as connection:
            connection.execute(text('DROP TABLE IF EXISTS sales'))

        logging.info("Processing chunks...")
        for chunk in chunk_iterator:
            # Clean data
            cleaned_chunk = clean_data(chunk.copy()) # Use copy to avoid SettingWithCopyWarning
            
            # Generate insights from the chunk
            revenue_per_product = cleaned_chunk.groupby('product_id')['revenue'].sum()
            total_revenue_per_product = total_revenue_per_product.add(revenue_per_product, fill_value=0)
            
            # Store chunk in database
            cleaned_chunk.to_sql('sales', engine, if_exists='append', index=False)
        
        logging.info("All chunks processed.")

        # Finalize insights
        logging.info("Generating final insights...")
        top_10_products = total_revenue_per_product.nlargest(10)
        logging.info(f"Top 10 products by revenue:\n{top_10_products.to_string()}")
        
        # Create visualisation
        create_visualisation(top_10_products, VISUALISATION_FILE)
        
        logging.info(f"Data stored successfully in {DB_FILE}.")
        
    logging.info("Data pipeline finished.")

if __name__ == "__main__":
    main()