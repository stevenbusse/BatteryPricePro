import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

def interpolate_price(battery_df, voltage, kw, kwh, hours):
    """
    Calculate the estimated price for a custom battery configuration using
    interpolation based on known pre-configured models.
    
    Parameters:
    -----------
    battery_df : pandas.DataFrame
        DataFrame containing pre-configured battery models with columns:
        'voltage', 'kW', 'kWh', 'backup_hours', and 'price'
    voltage : float
        Voltage rating for the custom configuration (208V or 480V)
    kw : float
        Power in kilowatts (kW) for the custom configuration
    kwh : float
        Energy in kilowatt-hours (kWh) for the custom configuration
    hours : float
        Backup duration in hours for the custom configuration
        
    Returns:
    --------
    float
        Estimated price for the custom battery configuration
    """
    # First filter by voltage to ensure we're only comparing within the same voltage class
    filtered_df = battery_df[battery_df['voltage'] == voltage]
    
    # If no models match the voltage, return None or raise an error
    if filtered_df.empty:
        raise ValueError(f"No pre-configured models found for voltage {voltage}V")
    
    # Extract the feature points (kW, kWh, backup_hours) and target values (price)
    points = filtered_df[['kW', 'kWh', 'backup_hours']].values
    prices = filtered_df['price'].values
    
    # Create the interpolator
    # First try linear interpolation
    interpolator = LinearNDInterpolator(points, prices)
    
    # Query the interpolator for the custom configuration
    estimated_price = float(interpolator([kw, kwh, hours]))
    
    # If linear interpolation fails (returns NaN), use nearest neighbor interpolation
    if np.isnan(estimated_price):
        nearest_interpolator = NearestNDInterpolator(points, prices)
        estimated_price = float(nearest_interpolator([kw, kwh, hours]))
        
    return estimated_price
