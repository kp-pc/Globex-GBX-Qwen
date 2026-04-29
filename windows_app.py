"""
Globex Windows Desktop Application Entry Point
Launches the web dashboard in a borderless window or default browser.
"""
import sys
import webbrowser
import threading
from dashboard import app

def open_dashboard():
    """Open the dashboard in the default browser after a short delay."""
    import time
    time.sleep(1.5)  # Wait for server to start
    webbrowser.open("http://127.0.0.1:5001")

if __name__ == "__main__":
    print("🚀 Starting Globex Wallet for Windows...")
    # Start the browser in a separate thread
    threading.Thread(target=open_dashboard, daemon=True).start()
    
    # Run the flask app
    # debug=False is crucial for production/exe builds
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
