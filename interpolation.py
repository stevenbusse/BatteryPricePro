import numpy as np
import pandas as pd

def interpolate_price(battery_df, voltage, kw, kwh, hours, include_tariff=True, module_size=10.24, tariff_percentage=73.8):
    """
    Calculate the estimated price for a custom battery configuration using
    exact interpolation between the models with kW values above and below the target.
    
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
    filtered_df = battery_df[battery_df['voltage'] == voltage].copy()
    
    # If no models match the voltage, return None or raise an error
    if filtered_df.empty:
        raise ValueError(f"No pre-configured models found for voltage {voltage}V")
    
    # Calculate the number of modules needed for the requested kWh
    # Use integer ceiling (round up) to ensure enough modules
    modules_needed = int(np.ceil(kwh / module_size))
    
    # Add module count to each pre-configured model
    filtered_df.loc[:, 'modules'] = np.ceil(filtered_df['kWh'] / module_size).astype(int)
    
    # First, try to find models with matching kW rating
    models_by_kw = filtered_df[filtered_df['kW'] == kw]
    
    # If no exact kW match, find closest above and below for kW
    if models_by_kw.empty:
        models_above_kw = filtered_df[filtered_df['kW'] > kw].sort_values('kW')
        models_below_kw = filtered_df[filtered_df['kW'] < kw].sort_values('kW', ascending=False)
        
        if not models_above_kw.empty:
            kw_above = models_above_kw.iloc[0]['kW']
            models_above_kw = filtered_df[filtered_df['kW'] == kw_above]
        
        if not models_below_kw.empty:
            kw_below = models_below_kw.iloc[0]['kW']
            models_below_kw = filtered_df[filtered_df['kW'] == kw_below]
            
        # If we have models both above and below, use both for kW range
        if not models_above_kw.empty and not models_below_kw.empty:
            models_by_kw = pd.concat([models_above_kw, models_below_kw])
        # Otherwise use what we have
        elif not models_above_kw.empty:
            models_by_kw = models_above_kw
        elif not models_below_kw.empty:
            models_by_kw = models_below_kw
    
    # Now find models with module counts above and below our target
    # But only within the appropriate kW range we identified
    models_by_kw_sorted = models_by_kw.sort_values('modules')
    
    # Find the upper and lower models for interpolation based on module count
    model_above = None
    model_below = None
    
    # Find model above (with modules >= target)
    models_above = models_by_kw_sorted[models_by_kw_sorted['modules'] >= modules_needed]
    if not models_above.empty:
        model_above = models_above.iloc[0]
    
    # Find model below (with modules < target)
    models_below = models_by_kw_sorted[models_by_kw_sorted['modules'] < modules_needed]
    if not models_below.empty:
        model_below = models_below.iloc[-1]  # Get the highest module count below target
    
    # Calculate price based on interpolation between models above and below
    without_tariff_estimated = 0
    upper_price = 0
    lower_price = 0
    
    # Case 1: We have models both above and below
    if model_above is not None and model_below is not None:
        # Get module counts and prices
        upper_modules = model_above['modules']
        lower_modules = model_below['modules']
        upper_price = model_above['price_without_tariff']
        lower_price = model_below['price_without_tariff']
        
        # Calculate price difference per module in the gap
        module_diff = upper_modules - lower_modules
        price_diff = upper_price - lower_price
        
        if module_diff > 0:
            # Price per module in the gap between models
            price_per_module_in_gap = price_diff / module_diff
            
            # Calculate price by adding the appropriate amount above the lower model
            modules_from_lower = modules_needed - lower_modules
            price_adjustment = modules_from_lower * price_per_module_in_gap
            without_tariff_estimated = lower_price + price_adjustment
        else:
            # If models have same module count (shouldn't happen), use average price
            without_tariff_estimated = (upper_price + lower_price) / 2
    
    # Case 2: We only have a model below
    elif model_below is not None:
        # Use the price per module from the model below and extrapolate
        lower_modules = model_below['modules']
        lower_price = model_below['price_without_tariff']
        
        # If we have another model with the same kW, try to find price per module pattern
        same_kw_models = filtered_df[filtered_df['kW'] == model_below['kW']].sort_values('modules')
        
        if len(same_kw_models) > 1:
            # Find the next highest module count model to calculate gap price
            higher_models = same_kw_models[same_kw_models['modules'] > lower_modules]
            if not higher_models.empty:
                next_higher = higher_models.iloc[0]
                module_diff = next_higher['modules'] - lower_modules
                price_diff = next_higher['price_without_tariff'] - lower_price
                
                if module_diff > 0:
                    price_per_module_in_gap = price_diff / module_diff
                    modules_to_add = modules_needed - lower_modules
                    without_tariff_estimated = lower_price + (modules_to_add * price_per_module_in_gap)
                else:
                    # Fallback if module counts are the same
                    price_per_module = lower_price / lower_modules
                    without_tariff_estimated = price_per_module * modules_needed
            else:
                # No higher model with same kW, use average price per module
                price_per_module = lower_price / lower_modules
                without_tariff_estimated = price_per_module * modules_needed
        else:
            # Only one model with this kW, use its price per module
            price_per_module = lower_price / lower_modules
            without_tariff_estimated = price_per_module * modules_needed
    
    # Case 3: We only have a model above
    elif model_above is not None:
        # Use the price per module from the model above and extrapolate down
        upper_modules = model_above['modules']
        upper_price = model_above['price_without_tariff']
        
        # If we have another model with the same kW, try to find price per module pattern
        same_kw_models = filtered_df[filtered_df['kW'] == model_above['kW']].sort_values('modules')
        
        if len(same_kw_models) > 1:
            # Find the next lowest module count model to calculate gap price
            lower_models = same_kw_models[same_kw_models['modules'] < upper_modules]
            if not lower_models.empty:
                next_lower = lower_models.iloc[-1]  # Get highest of the lower models
                module_diff = upper_modules - next_lower['modules']
                price_diff = upper_price - next_lower['price_without_tariff']
                
                if module_diff > 0:
                    price_per_module_in_gap = price_diff / module_diff
                    modules_to_subtract = upper_modules - modules_needed
                    without_tariff_estimated = upper_price - (modules_to_subtract * price_per_module_in_gap)
                else:
                    # Fallback if module counts are the same
                    price_per_module = upper_price / upper_modules
                    without_tariff_estimated = price_per_module * modules_needed
            else:
                # No lower model with same kW, use average price per module
                price_per_module = upper_price / upper_modules
                without_tariff_estimated = price_per_module * modules_needed
        else:
            # Only one model with this kW, use its price per module
            price_per_module = upper_price / upper_modules
            without_tariff_estimated = price_per_module * modules_needed
    
    # Case 4: No suitable models found - use global average price per module as last resort
    else:
        # Calculate average price per module across all models with this voltage
        filtered_df['price_per_module'] = filtered_df['price_without_tariff'] / filtered_df['modules']
        avg_price_per_module = filtered_df['price_per_module'].mean()
        without_tariff_estimated = avg_price_per_module * modules_needed
    
    # Apply the tariff percentage to calculate the tariff amount
    tariff_amount = without_tariff_estimated * (tariff_percentage / 100)
    
    # Calculate total price with tariff
    with_tariff_estimated = without_tariff_estimated + tariff_amount
    
    # Calculate price per module for display
    price_per_module = without_tariff_estimated / modules_needed if modules_needed > 0 else 0
    
    # Create result dictionary
    price_estimates = {
        'with_tariff': with_tariff_estimated,
        'without_tariff': without_tariff_estimated,
        'tariff_only': tariff_amount,
        'tariff_percentage': tariff_percentage,
        'modules_needed': modules_needed,
        'price_per_module': price_per_module,
        'upper_price': upper_price,
        'lower_price': lower_price,
        'interpolation_method': 'exact_gap'
    }
    
    # If tariff should not be included, set the with_tariff price equal to without_tariff
    if not include_tariff:
        price_estimates['with_tariff'] = price_estimates['without_tariff']
        price_estimates['tariff_only'] = 0.0
    
    return price_estimates
