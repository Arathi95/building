
import pandas as pd
from datetime import timedelta

def calculate_rfm(df):
    """
    Calculates RFM (Recency, Frequency, Monetary) scores for each customer.

    Args:
        df: The input pandas DataFrame with transaction data.

    Returns:
        A pandas DataFrame with RFM scores.
    """
    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    })
    rfm.rename(columns={'InvoiceDate': 'Recency',
                        'InvoiceNo': 'Frequency',
                        'TotalPrice': 'MonetaryValue'}, inplace=True)

    # Handle cases with too few unique values for qcut
    for col, labels in zip(['Recency', 'Frequency', 'MonetaryValue'], [range(4, 0, -1), range(1, 5), range(1, 5)]):
        try:
            # Use rank(method='first') to handle ties
            rfm[col[0]] = pd.qcut(rfm[col].rank(method='first'), q=4, labels=labels).astype(int)
        except ValueError:
            # If qcut fails, assign a default score (e.g., middle score)
            # This can happen if there are very few unique values
            rfm[col[0]] = 2 # Assign a neutral score

    rfm['RFM_Segment'] = rfm.apply(lambda x: str(x['R']) + str(x['F']) + str(x['M']), axis=1)
    rfm['RFM_Score'] = rfm[['R', 'F', 'M']].sum(axis=1)

    return rfm

def get_rfm_segment_meaning(row):
    """Assigns a descriptive segment name based on RFM scores."""
    if row['R'] >= 4 and row['F'] >= 4 and row['M'] >= 4:
        return 'Best Customers'
    elif row['R'] >= 3 and row['F'] >= 3:
        return 'Loyal Customers'
    elif row['R'] >= 3 and row['M'] >= 3:
        return 'Big Spenders'
    elif row['R'] <= 2 and row['F'] <= 2:
        return 'At Risk'
    elif row['R'] <= 2:
        return 'Needs Attention'
    else:
        return 'Others'

def calculate_clv(df):
    """
    Calculates Customer Lifetime Value (CLV).

    Args:
        df: The input pandas DataFrame.

    Returns:
        A pandas DataFrame with CLV calculated for each customer.
    """
    clv_df = df.groupby('CustomerID').agg(
        total_transactions=('InvoiceNo', 'nunique'),
        total_products=('Quantity', 'sum'),
        total_revenue=('TotalPrice', 'sum'),
        first_purchase_date=('InvoiceDate', 'min'),
        last_purchase_date=('InvoiceDate', 'max')
    )
    clv_df['purchase_lifespan'] = (clv_df['last_purchase_date'] - clv_df['first_purchase_date']).dt.days
    clv_df['avg_order_value'] = clv_df['total_revenue'] / clv_df['total_transactions']
    clv_df['purchase_frequency'] = clv_df['total_transactions'] / (clv_df['purchase_lifespan'] + 1)
    clv_df['clv'] = clv_df['avg_order_value'] * clv_df['purchase_frequency'] * 365  # Assuming a 1-year projection
    return clv_df.sort_values(by='clv', ascending=False)

def get_sales_trends(df, freq='M'):
    """
    Calculates sales trends over time.

    Args:
        df: The input pandas DataFrame.
        freq: The frequency for resampling (e.g., 'D' for daily, 'W' for weekly, 'M' for monthly).

    Returns:
        A pandas Series with sales data over time.
    """
    sales_trends = df.set_index('InvoiceDate')['TotalPrice'].resample(freq).sum()
    return sales_trends

def get_top_products(df, top_n=10):
    """
    Gets the top N selling products.

    Args:
        df: The input pandas DataFrame.
        top_n: The number of top products to return.

    Returns:
        A pandas DataFrame of the top selling products.
    """
    top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(top_n)
    return top_products

def get_geographic_distribution(df):
    """
    Calculates sales distribution by country.

    Args:
        df: The input pandas DataFrame.

    Returns:
        A pandas DataFrame with sales data by country.
    """
    geo_dist = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
    return geo_dist
