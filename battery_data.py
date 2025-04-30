import pandas as pd

def get_battery_data():
    """
    Returns a DataFrame containing the pre-configured battery models
    with their specifications: kW, kWh, backup hours, and price.
    
    Each row represents a pre-configured battery model.
    """
    # Define the pre-configured battery models
    # Note: These are example values. Replace with actual data.
    data = [
        # Model 1
        {'kW': 10, 'kWh': 20, 'backup_hours': 2.0, 'price': 15000},
        # Model 2
        {'kW': 15, 'kWh': 30, 'backup_hours': 2.0, 'price': 21000},
        # Model 3
        {'kW': 20, 'kWh': 40, 'backup_hours': 2.0, 'price': 27000},
        # Model 4
        {'kW': 25, 'kWh': 50, 'backup_hours': 2.0, 'price': 32500},
        # Model 5
        {'kW': 30, 'kWh': 60, 'backup_hours': 2.0, 'price': 38000},
        # Model 6
        {'kW': 10, 'kWh': 40, 'backup_hours': 4.0, 'price': 20000},
        # Model 7
        {'kW': 15, 'kWh': 60, 'backup_hours': 4.0, 'price': 28000},
        # Model 8
        {'kW': 20, 'kWh': 80, 'backup_hours': 4.0, 'price': 36000},
        # Model 9
        {'kW': 25, 'kWh': 100, 'backup_hours': 4.0, 'price': 44000},
        # Model 10
        {'kW': 30, 'kWh': 120, 'backup_hours': 4.0, 'price': 52000},
        # Model 11
        {'kW': 10, 'kWh': 60, 'backup_hours': 6.0, 'price': 24000},
        # Model 12
        {'kW': 15, 'kWh': 90, 'backup_hours': 6.0, 'price': 35000},
        # Model 13
        {'kW': 20, 'kWh': 120, 'backup_hours': 6.0, 'price': 46000},
        # Model 14
        {'kW': 25, 'kWh': 150, 'backup_hours': 6.0, 'price': 57000},
        # Model 15
        {'kW': 30, 'kWh': 180, 'backup_hours': 6.0, 'price': 68000},
    ]
    
    # Create DataFrame from the data
    df = pd.DataFrame(data)
    
    # Add model names for better identification
    df['model_name'] = [f"Model {i+1}" for i in range(len(df))]
    
    # Reorder columns to put model_name first
    cols = ['model_name', 'kW', 'kWh', 'backup_hours', 'price']
    df = df[cols]
    
    return df
