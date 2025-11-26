import os
import time
import random
import logging
import argparse
from datetime import datetime
from pathlib import Path # Pathlib handles OS-specific path separators

# --- Configuration ---
SERVICES = ["auth_service", "payment_gateway"]
LEVELS = ["INFO", "INFO", "INFO", "WARNING", "ERROR"]
MESSAGES = {
    "INFO": ["User login successful", "Transaction started", "Health check passed", "Page rendered"],
    "WARNING": ["High memory usage", "Response time > 500ms", "Disk space low", "Deprecation warning"],
    "ERROR": ["Database connection failed", "Payment declined", "NullPointerException", "Timeout waiting for upstream"]
}

# Variable to hold the dynamic path, initialized later
LOG_DIR = None 

def setup_environment():
    """Ensures the log directory and files exist."""
    # Use the global LOG_DIR variable
    global LOG_DIR 

    # Pathlib handles cross-platform directory creation seamlessly
    if not LOG_DIR.exists():
        # Using parents=True and exist_ok=True ensures robustness
        LOG_DIR.mkdir(parents=True, exist_ok=True) 
        # .absolute() ensures the user sees the full, correct path for their OS
        print(f"[Setup] Created directory: {LOG_DIR.resolve().absolute()}")
    
    # Create empty files if they don't exist
    for service in SERVICES:
        file_path = LOG_DIR / f"{service}.log"
        if not file_path.exists():
            file_path.touch()
            print(f"[Setup] Created log file: {file_path.name}")

def write_log_entry():
    """Selects a random service and writes a random log line."""
    service = random.choice(SERVICES)
    level = random.choice(LEVELS)
    message = random.choice(MESSAGES[level])
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    file_path = LOG_DIR / f"{service}.log" 
    
    with open(file_path, "a") as f:
        f.write(log_entry)
    
    print(f"Written to {service}.log in {LOG_DIR.name}: {level}")

def main():
    """Handles argument parsing and starts the log generation."""
    global LOG_DIR
    
    # 1. Setup Argument Parser
    parser = argparse.ArgumentParser(
        description="A dynamic log file generator for testing log processors."
    )
    # 2. Define the optional input parameter
    parser.add_argument(
        "--path",
        type=str,
        # *** KEY CHANGE: Use a RELATIVE PATH as the default ***
        default="live_logs", 
        help="The directory path where log files will be created (e.g., live_logs or C:\\temp\\my_logs)"
    )
    
    args = parser.parse_args()
    
    # 3. Set the global LOG_DIR using the Path object
    # pathlib will correctly interpret the path using the OS's file separators
    LOG_DIR = Path(args.path)

    print(f"--- Log Generator Started (Logs Path: {LOG_DIR.resolve().absolute()}) ---")
    setup_environment()
    
    try:
        while True:
            write_log_entry()
            time.sleep(random.uniform(0.1, 1.5))
    except KeyboardInterrupt:
        print("\n--- Generator Stopped ---")

if __name__ == "__main__":
    main()