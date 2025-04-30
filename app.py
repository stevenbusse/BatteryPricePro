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

col1, col2 = st.columns(2)

with col1:
    # User inputs for custom configuration
    kw_input = st.number_input("Power (kW)", 
                               min_value=float(battery_df['kW'].min()), 
                               max_value=float(battery_df['kW'].max()),
                               step=0.1,
                               help="Enter the desired power in kilowatts (kW)")

    kwh_input = st.number_input("Energy (kWh)", 
                                min_value=float(battery_df['kWh'].min()), 
                                max_value=float(battery_df['kWh'].max()),
                                step=0.1,
                                help="Enter the desired energy capacity in kilowatt-hours (kWh)")

with col2:
    # Calculate backup hours but allow user to override
    if kw_input > 0:
        calculated_hours = kwh_input / kw_input
    else:
        calculated_hours = 0
        
    hours_input = st.number_input("Backup Hours", 
                                  min_value=float(battery_df['backup_hours'].min()), 
                                  max_value=float(battery_df['backup_hours'].max()),
                                  value=float(calculated_hours),
                                  step=0.1,
                                  help="Enter the desired backup duration in hours")
    
    # Show automatically calculated backup hours
    st.write(f"Calculated backup hours: {calculated_hours:.2f} hours")

# Calculate price button
if st.button("Calculate Price"):
    try:
        # Validate inputs
        if kw_input <= 0 or kwh_input <= 0 or hours_input <= 0:
            st.error("All values must be greater than zero.")
        else:
            # Check if inputs are within the range of pre-configured models
            kw_min, kw_max = battery_df['kW'].min(), battery_df['kW'].max()
            kwh_min, kwh_max = battery_df['kWh'].min(), battery_df['kWh'].max()
            hours_min, hours_max = battery_df['backup_hours'].min(), battery_df['backup_hours'].max()
            
            if not (kw_min <= kw_input <= kw_max):
                st.warning(f"Power (kW) input is outside the range of pre-configured models ({kw_min} - {kw_max}). Extrapolation may be less accurate.")
                
            if not (kwh_min <= kwh_input <= kwh_max):
                st.warning(f"Energy (kWh) input is outside the range of pre-configured models ({kwh_min} - {kwh_max}). Extrapolation may be less accurate.")
                
            if not (hours_min <= hours_input <= hours_max):
                st.warning(f"Backup hours input is outside the range of pre-configured models ({hours_min} - {hours_max}). Extrapolation may be less accurate.")
            
            # Perform interpolation
            estimated_price = interpolate_price(
                battery_df, 
                kw_input, 
                kwh_input, 
                hours_input
            )
            
            # Display the result
            st.success(f"Estimated Price: ${estimated_price:,.2f}")
            
            # Show custom configuration details
            st.subheader("Custom Configuration Details")
            custom_config = pd.DataFrame({
                'kW': [kw_input],
                'kWh': [kwh_input],
                'backup_hours': [hours_input],
                'estimated_price': [estimated_price]
            })
            st.dataframe(custom_config)
            
    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")

# Add information about the calculation method
st.sidebar.header("About the Calculator")
st.sidebar.write("""
This calculator uses interpolation to estimate prices for custom battery cabinet configurations.

**How it works:**
1. We store data for pre-configured battery models with known prices
2. When you input custom specifications, the algorithm:
   - Finds similar pre-configured models
   - Calculates the price based on the relative position of your configuration
   - Considers multiple dimensions (kW, kWh, backup hours)

The more your custom configuration differs from pre-configured models, the less accurate the price estimate may be.
""")
