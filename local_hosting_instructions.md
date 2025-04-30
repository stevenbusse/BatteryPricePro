# Local Hosting Instructions for Battery Calculator

This document provides instructions for hosting the Battery Cabinet Pricing Calculator on a local network, allowing multiple team members to access it without each needing to install Python or an IDE.

## Prerequisites

The host computer needs to have:
1. Python 3.8 or newer installed
2. Required Python packages: `streamlit`, `pandas`, `numpy`

## Installation Steps (Host Computer)

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install required packages**
   ```
   pip install streamlit pandas numpy
   ```

3. **Download the calculator files**
   - Place all the project files in a folder:
     - `app.py`
     - `battery_data.py`
     - `interpolation.py`
     - `.streamlit/config.toml`

## Running the Application for Local Network Access

1. **Find your computer's local IP address**
   - On Windows: Open Command Prompt and type `ipconfig`
   - On Mac/Linux: Open Terminal and type `ifconfig` or `ip addr`
   - Look for the IPv4 address (typically starts with 192.168.x.x or 10.x.x.x)

2. **Run Streamlit with network access**
   ```
   streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   ```

3. **Access from other computers**
   - Other team members can access the calculator by opening a web browser
   - Enter the URL: `http://[HOST-IP-ADDRESS]:8501`
   - Replace `[HOST-IP-ADDRESS]` with the actual IP address from step 1

## Making this a Permanent Solution

For a more permanent solution without needing to run commands:

1. **Create a batch file (Windows) or shell script (Mac/Linux)**
   
   **For Windows (start_calculator.bat)**:
   ```
   @echo off
   echo Starting Battery Calculator Server...
   echo Access it at http://localhost:8501 (this computer)
   echo.
   for /f "tokens=4" %%a in ('route print ^| find " 0.0.0.0"') do (
     if not "%%a"=="0.0.0.0" (
       echo For other computers, use: http://%%a:8501
       echo.
     )
   )
   python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   pause
   ```

   **For Mac/Linux (start_calculator.sh)**:
   ```bash
   #!/bin/bash
   echo "Starting Battery Calculator Server..."
   echo "Access it at http://localhost:8501 (this computer)"
   echo ""
   ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}')
   echo "For other computers, use: http://$ip:8501"
   echo ""
   python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   ```

2. **Make the script executable (Mac/Linux only)**
   ```
   chmod +x start_calculator.sh
   ```

3. **Create desktop shortcut to the script**
   - Right-click the script file and create shortcut
   - Place the shortcut on the desktop for easy access

## Troubleshooting

1. **Firewall issues**
   - If team members cannot access the app, check if the host computer's firewall is blocking port 8501
   - Add an exception for port 8501 in the firewall settings

2. **Different network segments**
   - All computers must be on the same local network segment
   - VPN connections may interfere with local network discovery

3. **Alternative port**
   - If port 8501 is already in use, try a different port:
   ```
   streamlit run app.py --server.address=0.0.0.0 --server.port=8502
   ```
   - Update the access URL accordingly to use the new port

## Additional Options

For an even more permanent solution, consider:

1. **Setting up the application as a service** so it starts automatically with the computer
2. **Using Docker** to containerize the application for easier deployment
3. **Hosting on a small server** like a Raspberry Pi that can run 24/7 with minimal power consumption