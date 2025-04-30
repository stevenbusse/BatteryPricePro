import pandas as pd

def get_battery_data():
    """
    Returns a DataFrame containing the pre-configured battery models
    with their specifications: voltage, kW, kWh, backup hours, and price.
    
    Each row represents a pre-configured battery model.
    """
    # Define the pre-configured battery models with actual data
    data = [
        # Model 1
        {'voltage': 208, 'kW': 30, 'kWh': 81, 'backup_hours': 2.7, 'price': 90000},
        # Model 2
        {'voltage': 208, 'kW': 30, 'kWh': 122, 'backup_hours': 4.1, 'price': 105100},
        # Model 3
        {'voltage': 208, 'kW': 30, 'kWh': 184, 'backup_hours': 6.1, 'price': 133300},
        # Model 4
        {'voltage': 208, 'kW': 50, 'kWh': 122, 'backup_hours': 2.4, 'price': 123000},
        # Model 5
        {'voltage': 208, 'kW': 50, 'kWh': 184, 'backup_hours': 3.7, 'price': 151300},
        # Model 6
        {'voltage': 208, 'kW': 50, 'kWh': 245, 'backup_hours': 4.9, 'price': 173900},
        # Model 7
        {'voltage': 480, 'kW': 30, 'kWh': 81, 'backup_hours': 2.7, 'price': 90000},
        # Model 8
        {'voltage': 480, 'kW': 30, 'kWh': 122, 'backup_hours': 4.1, 'price': 105100},
        # Model 9
        {'voltage': 480, 'kW': 30, 'kWh': 184, 'backup_hours': 6.1, 'price': 133300},
        # Model 10
        {'voltage': 480, 'kW': 60, 'kWh': 122, 'backup_hours': 2.0, 'price': 123000},
        # Model 11
        {'voltage': 480, 'kW': 60, 'kWh': 184, 'backup_hours': 3.1, 'price': 151300},
        # Model 12
        {'voltage': 480, 'kW': 60, 'kWh': 245, 'backup_hours': 4.1, 'price': 173900},
        # Model 13
        {'voltage': 480, 'kW': 90, 'kWh': 184, 'backup_hours': 2.0, 'price': 166800},
        # Model 14
        {'voltage': 480, 'kW': 90, 'kWh': 245, 'backup_hours': 2.7, 'price': 189500},
        # Model 15
        {'voltage': 480, 'kW': 90, 'kWh': 266, 'backup_hours': 3.0, 'price': 197000},
    ]
    
    # Create DataFrame from the data
    df = pd.DataFrame(data)
    
    # Add model names for better identification
    df['model_name'] = [f"Model {i+1}" for i in range(len(df))]
    
    # Reorder columns to put model_name first
    cols = ['model_name', 'voltage', 'kW', 'kWh', 'backup_hours', 'price']
    df = df[cols]
    
    return df
