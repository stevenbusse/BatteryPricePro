import numpy as np
import pandas as pd

def interpolate_price(battery_df, voltage, kw, kwh, hours, include_tariff=True, module_size=10.24):
    """
    Calculate the estimated price for a custom battery configuration using
    a module-based approach. The price is calculated based on finding models 
    with similar kW ratings, calculating the price per module, and then 
    multiplying by the number of modules needed.
    
    Parameters:
    -----------
    battery_df : pandas.DataFrame
        DataFrame containing pre-configured battery models with columns:
        'voltage', 'kW', 'kWh', 'backup_hours', 'price_with_tariff', and 'price_without_tariff'
    voltage : float
        Voltage rating for the custom configuration (208V or 480V)
    kw : float
        Power in kilowatts (kW) for the custom configuration
    kwh : float
        Energy in kilowatt-hours (kWh) for the custom configuration
    hours : float
        Backup duration in hours for the custom configuration
    include_tariff : bool, default=True
        Whether to include tariff in the price calculation
    module_size : float, default=10.24
        The energy capacity (kWh) of a single battery module
        
    Returns:
    --------
    dict
        Dictionary containing 'with_tariff', 'without_tariff', 'tariff_only', and 'modules_needed' estimates
    """
    # First filter by voltage to ensure we're only comparing within the same voltage class
    filtered_df = battery_df[battery_df['voltage'] == voltage]
    
    # If no models match the voltage, return None or raise an error
    if filtered_df.empty:
        raise ValueError(f"No pre-configured models found for voltage {voltage}V")
    
    # Filter by kW range - first find closest kW matches
    models_by_kw = filtered_df.loc[filtered_df['kW'] == kw]
    
    # If no exact kW match, find closest above and below
    if models_by_kw.empty:
        models_above_kw = filtered_df.loc[filtered_df['kW'] > kw].sort_values('kW')
        models_below_kw = filtered_df.loc[filtered_df['kW'] < kw].sort_values('kW', ascending=False)
        
        if not models_above_kw.empty:
            kw_above = models_above_kw.iloc[0]['kW']
            models_above_kw = filtered_df.loc[filtered_df['kW'] == kw_above]
        
        if not models_below_kw.empty:
            kw_below = models_below_kw.iloc[0]['kW']
            models_below_kw = filtered_df.loc[filtered_df['kW'] == kw_below]
            
        # If we have models both above and below, use both
        if not models_above_kw.empty and not models_below_kw.empty:
            models_by_kw = pd.concat([models_above_kw, models_below_kw])
        # Otherwise use what we have
        elif not models_above_kw.empty:
            models_by_kw = models_above_kw
        elif not models_below_kw.empty:
            models_by_kw = models_below_kw
    
    # Calculate the number of modules needed for the requested kWh
    # Use integer ceiling (round up) to ensure enough modules
    modules_needed = int(np.ceil(kwh / module_size))
    
    # Calculate the estimated price based on module count
    # 1. Calculate price per module for each model
    models_by_kw['modules'] = np.ceil(models_by_kw['kWh'] / module_size)
    models_by_kw['price_with_tariff_per_module'] = models_by_kw['price_with_tariff'] / models_by_kw['modules']
    models_by_kw['price_without_tariff_per_module'] = models_by_kw['price_without_tariff'] / models_by_kw['modules']
    
    # 2. Calculate average price per module
    avg_price_with_tariff_per_module = models_by_kw['price_with_tariff_per_module'].mean()
    avg_price_without_tariff_per_module = models_by_kw['price_without_tariff_per_module'].mean()
    
    # 3. Calculate final price based on modules needed
    with_tariff_estimated = avg_price_with_tariff_per_module * modules_needed
    without_tariff_estimated = avg_price_without_tariff_per_module * modules_needed
    
    # Create result dictionary
    price_estimates = {
        'with_tariff': with_tariff_estimated,
        'without_tariff': without_tariff_estimated,
        'tariff_only': with_tariff_estimated - without_tariff_estimated,
        'modules_needed': modules_needed
    }
    
    return price_estimates
