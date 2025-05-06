import subprocess
import os
import sys
import webbrowser

# Get path to app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "app.py")
port = "8501"
local_url = f"http://localhost:{port}"

try:
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", script_path,
        "--server.address=127.0.0.1",
        f"--server.port={port}"
    ])
    webbrowser.open(local_url)

except Exception as e:
    import traceback
    traceback.print_exc()
    input("Error occurred. Press Enter to close...")
    sys.exit(1)
