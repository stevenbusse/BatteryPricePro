import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

def interpolate_price(battery_df, voltage, kw, kwh, hours, include_tariff=True):
    """
    Calculate the estimated price for a custom battery configuration using
    interpolation based on known pre-configured models.
    
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
        
    Returns:
    --------
    dict
        Dictionary containing 'with_tariff', 'without_tariff', and 'tariff_only' price estimates
    """
    # First filter by voltage to ensure we're only comparing within the same voltage class
    filtered_df = battery_df[battery_df['voltage'] == voltage]
    
    # If no models match the voltage, return None or raise an error
    if filtered_df.empty:
        raise ValueError(f"No pre-configured models found for voltage {voltage}V")
    
    # Extract the feature points (kW, kWh, backup_hours)
    points = filtered_df[['kW', 'kWh', 'backup_hours']].values
    
    # Create result dictionary to store both price estimates
    price_estimates = {}
    
    # Interpolate price with tariff
    with_tariff_prices = filtered_df['price_with_tariff'].values
    with_tariff_interpolator = LinearNDInterpolator(points, with_tariff_prices)
    with_tariff_estimated = float(with_tariff_interpolator([kw, kwh, hours]))
    
    # If linear interpolation fails (returns NaN), use nearest neighbor interpolation
    if np.isnan(with_tariff_estimated):
        nearest_interpolator = NearestNDInterpolator(points, with_tariff_prices)
        with_tariff_estimated = float(nearest_interpolator([kw, kwh, hours]))
    
    price_estimates['with_tariff'] = with_tariff_estimated
    
    # Interpolate price without tariff
    without_tariff_prices = filtered_df['price_without_tariff'].values
    without_tariff_interpolator = LinearNDInterpolator(points, without_tariff_prices)
    without_tariff_estimated = float(without_tariff_interpolator([kw, kwh, hours]))
    
    # If linear interpolation fails (returns NaN), use nearest neighbor interpolation
    if np.isnan(without_tariff_estimated):
        nearest_interpolator = NearestNDInterpolator(points, without_tariff_prices)
        without_tariff_estimated = float(nearest_interpolator([kw, kwh, hours]))
    
    price_estimates['without_tariff'] = without_tariff_estimated
    
    # Calculate the estimated tariff
    price_estimates['tariff_only'] = with_tariff_estimated - without_tariff_estimated
    
    return price_estimates
