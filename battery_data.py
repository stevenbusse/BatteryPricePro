import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)


def get_battery_data():
    """
    Returns a DataFrame containing the pre-configured battery models
    with their specifications: voltage, kW, kWh, backup hours, price with tariff,
    and price without tariff.
    
    Each row represents a pre-configured battery model.
    """
    # Define the pre-configured battery models with actual data
    data = [
        # Model 1
        {'voltage': 208, 'kW': 30, 'kWh': 81, 'backup_hours': 2.7, 'price_with_tariff': 90000, 'price_without_tariff': 54700},
        # Model 2
        {'voltage': 208, 'kW': 30, 'kWh': 122, 'backup_hours': 4.1, 'price_with_tariff': 105100, 'price_without_tariff': 63000},
        # Model 3
        {'voltage': 208, 'kW': 30, 'kWh': 184, 'backup_hours': 6.1, 'price_with_tariff': 133300, 'price_without_tariff': 78400},
        # Model 4
        {'voltage': 208, 'kW': 50, 'kWh': 122, 'backup_hours': 2.4, 'price_with_tariff': 123000, 'price_without_tariff': 71400},
        # Model 5
        {'voltage': 208, 'kW': 50, 'kWh': 184, 'backup_hours': 3.7, 'price_with_tariff': 151300, 'price_without_tariff': 86800},
        # Model 6
        {'voltage': 208, 'kW': 50, 'kWh': 245, 'backup_hours': 4.9, 'price_with_tariff': 173900, 'price_without_tariff': 99100},
        # Model 7
        {'voltage': 480, 'kW': 30, 'kWh': 81, 'backup_hours': 2.7, 'price_with_tariff': 90000, 'price_without_tariff': 54700},
        # Model 8
        {'voltage': 480, 'kW': 30, 'kWh': 122, 'backup_hours': 4.1, 'price_with_tariff': 105100, 'price_without_tariff': 63000},
        # Model 9
        {'voltage': 480, 'kW': 30, 'kWh': 184, 'backup_hours': 6.1, 'price_with_tariff': 133300, 'price_without_tariff': 78400},
        # Model 10
        {'voltage': 480, 'kW': 60, 'kWh': 122, 'backup_hours': 2.0, 'price_with_tariff': 123000, 'price_without_tariff': 71400},
        # Model 11
        {'voltage': 480, 'kW': 60, 'kWh': 184, 'backup_hours': 3.1, 'price_with_tariff': 151300, 'price_without_tariff': 86800},
        # Model 12
        {'voltage': 480, 'kW': 60, 'kWh': 245, 'backup_hours': 4.1, 'price_with_tariff': 173900, 'price_without_tariff': 99100},
        # Model 13
        {'voltage': 480, 'kW': 90, 'kWh': 184, 'backup_hours': 2.0, 'price_with_tariff': 166800, 'price_without_tariff': 95300},
        # Model 14
        {'voltage': 480, 'kW': 90, 'kWh': 245, 'backup_hours': 2.7, 'price_with_tariff': 189500, 'price_without_tariff': 107600},
        # Model 15
        {'voltage': 480, 'kW': 90, 'kWh': 266, 'backup_hours': 3.0, 'price_with_tariff': 197000, 'price_without_tariff': 111700},
    ]
    
    # Create DataFrame from the data
    df = pd.DataFrame(data)
    
    # Calculate tariff for each model
    df['tariff'] = df['price_with_tariff'] - df['price_without_tariff']
    
    # Add model names for better identification
    df['model_name'] = [f"Model {i+1}" for i in range(len(df))]
    
    # Reorder columns to put model_name first
    cols = ['model_name', 'voltage', 'kW', 'kWh', 'backup_hours', 'price_with_tariff', 'price_without_tariff', 'tariff']
    df = df[cols]
    
    return df
