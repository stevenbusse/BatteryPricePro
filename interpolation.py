import numpy as np
import pandas as pd

def interpolate_price(battery_df, voltage, kw, kwh, hours, include_tariff=True, module_size=10.24, tariff_percentage=73.8):
    """
    Calculate the estimated price for a custom battery configuration using
    a module-based approach. The price is calculated based on interpolating between
    the models above and below in kW, calculating the price per module, and then 
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
    tariff_percentage : float, default=73.8
        The percentage to apply as tariff on the base price
        
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
    
    # Calculate the number of modules needed for the requested kWh
    # Use integer ceiling (round up) to ensure enough modules
    modules_needed = int(np.ceil(kwh / module_size))
    
    # Filter by kWh rather than kW - find the modules with kWh closest to our target
    filtered_df['modules'] = np.ceil(filtered_df['kWh'] / module_size).astype(int)
    filtered_df['price_without_tariff_per_module'] = filtered_df['price_without_tariff'] / filtered_df['modules']
    
    # Find models with module counts above and below our target
    models_above_kwh = filtered_df[filtered_df['modules'] >= modules_needed].sort_values('modules')
    models_below_kwh = filtered_df[filtered_df['modules'] < modules_needed].sort_values('modules', ascending=False)
    
    # Initialize price per module
    price_per_module = None
    
    # Case 1: We have models both above and below
    if not models_above_kwh.empty and not models_below_kwh.empty:
        model_above = models_above_kwh.iloc[0]
        model_below = models_below_kwh.iloc[0]
        
        # Interpolate price per module based on the difference in module count
        module_diff = model_above['modules'] - model_below['modules']
        if module_diff > 0:
            position = (modules_needed - model_below['modules']) / module_diff
            price_per_module = (
                model_below['price_without_tariff_per_module'] +
                position * (model_above['price_without_tariff_per_module'] - model_below['price_without_tariff_per_module'])
            )
        else:
            # If modules are the same, take the average
            price_per_module = (model_above['price_without_tariff_per_module'] + model_below['price_without_tariff_per_module']) / 2
    
    # Case 2: We only have models below
    elif not models_below_kwh.empty:
        # Use the closest model below
        model_below = models_below_kwh.iloc[0]
        price_per_module = model_below['price_without_tariff_per_module']
        
    # Case 3: We only have models above
    elif not models_above_kwh.empty:
        # Use the closest model above
        model_above = models_above_kwh.iloc[0]
        price_per_module = model_above['price_without_tariff_per_module']
    
    # Case 4: No models found - use a fallback average price
    if price_per_module is None:
        # Filter by kW to find similar models
        models_by_kw = filtered_df.copy()
        if not models_by_kw.empty:
            # If we have models with matching kW, use their average price per module
            price_per_module = models_by_kw['price_without_tariff_per_module'].mean()
        else:
            # Last resort - use an average from all models
            price_per_module = 3500  # Default fallback value if no suitable models are found
    
    # Calculate the base price
    without_tariff_estimated = price_per_module * modules_needed
    
    # Apply the tariff percentage to calculate the tariff amount
    tariff_amount = without_tariff_estimated * (tariff_percentage / 100)
    
    # Calculate total price with tariff
    with_tariff_estimated = without_tariff_estimated + tariff_amount
    
    # Create result dictionary
    price_estimates = {
        'with_tariff': with_tariff_estimated,
        'without_tariff': without_tariff_estimated,
        'tariff_only': tariff_amount,
        'tariff_percentage': tariff_percentage,
        'modules_needed': modules_needed,
        'price_per_module': price_per_module
    }
    
    # If tariff should not be included, set the with_tariff price equal to without_tariff
    if not include_tariff:
        price_estimates['with_tariff'] = price_estimates['without_tariff']
        price_estimates['tariff_only'] = 0.0
    
    return price_estimates
