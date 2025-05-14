import streamlit as st
import pandas as pd
import numpy as np
from battery_data import get_battery_data

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Battery Cabinet Pricing Calculator",
    page_icon="⚡",
    layout="centered"
)

# -----------------------------------
# Title and Intro
# -----------------------------------
st.title("Battery Cabinet Pricing Calculator")
st.write("""
This tool calculates the price of custom battery cabinet configurations based on 
pre-configured models and the number of battery modules required. Enter your 
desired specifications below.
""")

# -----------------------------------
# Load Battery Data
# -----------------------------------
battery_df = get_battery_data()

# Defensive check in case data is empty
if battery_df.empty:
    st.error("Battery data could not be loaded. Please check the data source.")
    st.stop()

# -----------------------------------
# Show Pre-configured Models
# -----------------------------------
with st.expander("View Pre-configured Battery Models"):
    st.dataframe(battery_df)

# -----------------------------------
# User Inputs
# -----------------------------------
st.subheader("Custom Configuration")
st.write("Enter your desired battery specifications:")

voltage_options = sorted(battery_df['voltage'].unique())
voltage_input = st.selectbox(
    "Voltage Rating", 
    options=voltage_options,
    help="Select the voltage rating for your battery cabinet"
)

filtered_df = battery_df[battery_df['voltage'] == voltage_input]

# If no matches found, exit early
if filtered_df.empty:
    st.error("No models found for selected voltage.")
    st.stop()

col1, col2, col3 = st.columns(3)

with col1:
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
    # Calculated backup hours, fallback to min if out of range
    calculated_hours = kwh_input / kw_input if kw_input > 0 else 0
    hours_min = float(filtered_df['backup_hours'].min())
    hours_max = float(filtered_df['backup_hours'].max())
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

    st.write(f"Calculated backup hours: {calculated_hours:.2f} hours")

# -----------------------------------
# Module Info
# -----------------------------------
st.subheader("Module Information")
module_size = 10.24  # kWh
st.write("Each battery module has a fixed capacity of 10.24 kWh and can support up to 90 kW of power.")

# -----------------------------------
# Tariff Controls
# -----------------------------------
st.subheader("Tariff Settings")
include_tariff = st.checkbox("Include tariffs in price calculation", value=True)

tariff_percentage = st.slider(
    "Tariff Percentage", 
    min_value=0.0, 
    max_value=100.0, 
    value=64.5,
    step=0.5,
    help="Adjust the tariff percentage applied to the base price"
)

# -----------------------------------
# Price Calculation
# -----------------------------------
if st.button("Calculate Price"):
    try:
        # Validate all inputs are positive
        if kw_input <= 0 or kwh_input <= 0 or hours_input <= 0 or module_size <= 0:
            st.error("All values must be greater than zero.")
            st.stop()

        # Warn user if any inputs are outside training range
        if not (filtered_df['kW'].min() <= kw_input <= filtered_df['kW'].max()):
            st.warning("Power (kW) input is outside known model range — extrapolation may reduce accuracy.")
        if not (filtered_df['kWh'].min() <= kwh_input <= filtered_df['kWh'].max()):
            st.warning("Energy (kWh) input is outside known model range — extrapolation may reduce accuracy.")
        if not (filtered_df['backup_hours'].min() <= hours_input <= filtered_df['backup_hours'].max()):
            st.warning("Backup hours input is outside known model range — extrapolation may reduce accuracy.")

        # Perform price interpolation
        price_estimates = interpolate_price(
            battery_df=battery_df, 
            voltage=voltage_input,
            kw=kw_input, 
            kwh=kwh_input, 
            hours=hours_input,
            include_tariff=include_tariff,
            module_size=module_size,
            tariff_percentage=tariff_percentage
        )

        # -----------------------------------
        # Display Pricing Output
        # -----------------------------------
        st.subheader("Estimated Pricing")

        col_left, col_right = st.columns(2)

        with col_left:
            st.success(f"Price with Tariff: ${price_estimates['with_tariff']:,.2f}")
            st.info(f"Price without Tariff: ${price_estimates['without_tariff']:,.2f}")
            st.write(f"**Modules Needed:** {price_estimates['modules_needed']}")
            if price_estimates.get('lower_price', 0) > 0:
                st.write(f"**Lower Model Price:** ${price_estimates['lower_price']:,.2f}")
            if price_estimates.get('upper_price', 0) > 0:
                st.write(f"**Upper Model Price:** ${price_estimates['upper_price']:,.2f}")

        with col_right:
            st.warning(f"Tariff Amount: ${price_estimates['tariff_only']:,.2f}")
            if price_estimates['without_tariff'] > 0:
                actual_pct = (price_estimates['tariff_only'] / price_estimates['without_tariff']) * 100
                st.write(f"Effective Tariff: {actual_pct:.2f}%")
            if price_estimates['modules_needed'] > 0:
                base_per_module = price_estimates.get('price_per_module', 0)
                final_per_module = price_estimates['with_tariff'] / price_estimates['modules_needed']
                st.write(f"**Base Price per Module:** ${base_per_module:,.2f}")
                st.write(f"**With Tariff per Module:** ${final_per_module:,.2f}")
                if 'interpolation_method' in price_estimates:
                    st.write(f"**Calculation Method:** Module-based interpolation")

        # -----------------------------------
        # Show Configuration Data
        # -----------------------------------
        st.subheader("Custom Configuration Details")
        custom_config = pd.DataFrame({
            'voltage': [voltage_input],
            'kW': [kw_input],
            'kWh': [kwh_input],
            'backup_hours': [hours_input],
            'modules_needed': [price_estimates['modules_needed']],
            'module_size_kWh': [module_size],
            'price_with_tariff': [price_estimates['with_tariff']],
            'price_without_tariff': [price_estimates['without_tariff']],
            'tariff_amount': [price_estimates['tariff_only']],
            'tariff_percentage': [tariff_percentage]
        })
        st.dataframe(custom_config)

    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")

# -----------------------------------
# Sidebar Help
# -----------------------------------
st.sidebar.header("About the Calculator")
st.sidebar.write("""
This calculator estimates prices for custom battery cabinet configurations based on the number of battery modules needed.

**How it works:**
- Filters battery models by voltage
- Uses interpolation to estimate price per module
- Calculates number of 10.24 kWh modules needed
- Applies tariff percentage to compute final cost

**About Tariffs:**
Tariffs represent import duties. You can toggle and adjust the percentage as needed.

**Note:** This is an estimation tool and actual project costs may vary depending on labor, freight, and installation.
""")
