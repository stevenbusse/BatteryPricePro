import streamlit as st
import pandas as pd
import numpy as np
from interpolation import interpolate_price
from battery_data import get_battery_data

# Page configuration
st.set_page_config(
    page_title="Battery Cabinet Pricing Calculator",
    page_icon="⚡",
    layout="centered"
)

# Application title and introduction
st.title("Battery Cabinet Pricing Calculator")
st.write("""
This tool calculates the price of custom battery cabinet configurations by interpolating 
between pre-configured models. Enter your desired specifications below.
""")

# Get pre-configured battery data
battery_df = get_battery_data()

# Display pre-configured models in a collapsible section
with st.expander("View Pre-configured Battery Models"):
    st.dataframe(battery_df)

# Input form for custom configuration
st.subheader("Custom Configuration")
st.write("Enter your desired battery specifications:")

# First let user select voltage
voltage_options = sorted(battery_df['voltage'].unique())
voltage_input = st.selectbox(
    "Voltage Rating", 
    options=voltage_options,
    help="Select the voltage rating for your battery cabinet"
)

# Filter models by selected voltage
filtered_df = battery_df[battery_df['voltage'] == voltage_input]

# Create 3 columns for the inputs
col1, col2, col3 = st.columns(3)

with col1:
    # User inputs for custom configuration
    kw_input = st.number_input(
        "Power (kW)", 
        min_value=float(filtered_df['kW'].min()), 
        max_value=float(filtered_df['kW'].max()),
        value=float(filtered_df['kW'].min()),
        step=5.0,
        help="Enter the desired power in kilowatts (kW)"
    )

with col2:
    kwh_input = st.number_input(
        "Energy (kWh)", 
        min_value=float(filtered_df['kWh'].min()), 
        max_value=float(filtered_df['kWh'].max()),
        value=float(filtered_df['kWh'].min()),
        step=10.0,
        help="Enter the desired energy capacity in kilowatt-hours (kWh)"
    )

with col3:
    # Calculate backup hours but allow user to override
    if kw_input > 0:
        calculated_hours = kwh_input / kw_input
    else:
        calculated_hours = 0
        
    hours_min = float(filtered_df['backup_hours'].min())
    hours_max = float(filtered_df['backup_hours'].max())
    
    # Make sure calculated_hours is within range, otherwise set to min
    if not (hours_min <= calculated_hours <= hours_max):
        calculated_hours = hours_min
        
    hours_input = st.number_input(
        "Backup Hours", 
        min_value=hours_min, 
        max_value=hours_max,
        value=calculated_hours,
        step=0.1,
        help="Enter the desired backup duration in hours"
    )
    
    # Show automatically calculated backup hours
    st.write(f"Calculated backup hours: {calculated_hours:.2f} hours")

# Add a checkbox for tariff inclusion
include_tariff = st.checkbox("Include tariffs in price calculation", value=True, 
                             help="Uncheck to see prices without tariffs")

# Calculate price button
if st.button("Calculate Price"):
    try:
        # Validate inputs
        if kw_input <= 0 or kwh_input <= 0 or hours_input <= 0:
            st.error("All values must be greater than zero.")
        else:
            # Check if inputs are within the range of pre-configured models
            kw_min, kw_max = filtered_df['kW'].min(), filtered_df['kW'].max()
            kwh_min, kwh_max = filtered_df['kWh'].min(), filtered_df['kWh'].max()
            hours_min, hours_max = filtered_df['backup_hours'].min(), filtered_df['backup_hours'].max()
            
            if not (kw_min <= kw_input <= kw_max):
                st.warning(f"Power (kW) input is outside the range of pre-configured models ({kw_min} - {kw_max}). Extrapolation may be less accurate.")
                
            if not (kwh_min <= kwh_input <= kwh_max):
                st.warning(f"Energy (kWh) input is outside the range of pre-configured models ({kwh_min} - {kwh_max}). Extrapolation may be less accurate.")
                
            if not (hours_min <= hours_input <= hours_max):
                st.warning(f"Backup hours input is outside the range of pre-configured models ({hours_min} - {hours_max}). Extrapolation may be less accurate.")
            
            # Perform interpolation
            price_estimates = interpolate_price(
                battery_df, 
                voltage_input,
                kw_input, 
                kwh_input, 
                hours_input,
                include_tariff
            )
            
            # Create columns for price display
            price_col1, price_col2 = st.columns(2)
            
            with price_col1:
                # Display the result with tariff
                st.success(f"Price with Tariff: ${price_estimates['with_tariff']:,.2f}")
                
                # Display the result without tariff
                st.info(f"Price without Tariff: ${price_estimates['without_tariff']:,.2f}")
            
            with price_col2:
                # Display the tariff amount
                st.warning(f"Tariff Amount: ${price_estimates['tariff_only']:,.2f}")
                
                # Show tariff percentage
                if price_estimates['without_tariff'] > 0:
                    tariff_percentage = (price_estimates['tariff_only'] / price_estimates['without_tariff']) * 100
                    st.write(f"Tariff Percentage: {tariff_percentage:.2f}%")
            
            # Show custom configuration details
            st.subheader("Custom Configuration Details")
            custom_config = pd.DataFrame({
                'voltage': [voltage_input],
                'kW': [kw_input],
                'kWh': [kwh_input],
                'backup_hours': [hours_input],
                'price_with_tariff': [price_estimates['with_tariff']],
                'price_without_tariff': [price_estimates['without_tariff']],
                'tariff_amount': [price_estimates['tariff_only']]
            })
            st.dataframe(custom_config)
            
    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")

# Add information about the calculation method
st.sidebar.header("About the Calculator")
st.sidebar.write("""
This calculator uses interpolation to estimate prices for custom battery cabinet configurations.

**How it works:**
1. We store data for pre-configured battery models with known prices (both with and without tariffs)
2. When you input custom specifications, the algorithm:
   - First filters by voltage rating
   - Finds similar pre-configured models
   - Calculates the price based on the relative position of your configuration
   - Considers multiple dimensions (kW, kWh, backup hours)
   - Calculates prices both with and without tariffs

**About Tariffs:**
Tariffs are additional costs applied to battery imports. The calculator provides pricing 
both with and without tariffs, allowing you to understand the full cost structure.

The more your custom configuration differs from pre-configured models, the less accurate the price estimate may be.
""")
