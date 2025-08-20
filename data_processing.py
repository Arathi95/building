import pandas as pd

def load_data(uploaded_file):
    """
    Loads data from the uploaded CSV file.

    Args:
        uploaded_file: The file uploaded by the user.

    Returns:
        A pandas DataFrame with the loaded data.
    """
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding='latin1')
            return df
        except Exception as e:
            return None
    return None

def clean_data(df):
    """
    Cleans the input DataFrame by handling missing values and duplicates.

    Args:
        df: The input pandas DataFrame.

    Returns:
        A cleaned pandas DataFrame.
    """
    df.dropna(subset=['CustomerID'], inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def transform_data(df):
    """
    Transforms the DataFrame by converting data types and creating new features.

    Args:
        df: The input pandas DataFrame.

    Returns:
        A transformed pandas DataFrame.
    """
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    return df

def validate_data(df):
    """
    Validates the presence of required columns in the DataFrame.

    Args:
        df: The pandas DataFrame to validate.

    Returns:
        A list of missing columns, or an empty list if all are present.
    """
    required_columns = ['InvoiceNo', 'StockCode', 'Description', 'Quantity',
                        'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns