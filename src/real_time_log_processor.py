import asyncio
import argparse
import sys
import time
from pathlib import Path
from typing import AsyncGenerator
from collections import deque, defaultdict

# --- Configuration ---
KEYWORDS = ["ERROR", "WARNING"]

# [ALGORITHM CONFIG]
# We look for density, not just counts.
# Example: "More than 3 errors in 15 seconds"
WINDOW_SIZE_SECONDS = 15
ALERT_THRESHOLD = 10

# --- Part 1: Robust File Tailing (Async I/O) ---
async def tail_file(filepath: Path) -> AsyncGenerator[str, None]:
    """
    Asynchronously monitors a file for new lines.
    Implements non-blocking I/O behavior similar to 'tail -f'.
    """
    try:
        with open(filepath, 'r') as f:
            # Move to end of file to ignore past history
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    # [ASYNC MODEL] Yield control to the event loop
                    await asyncio.sleep(0.1)
                    continue
                yield line.strip()
    except FileNotFoundError:
        await asyncio.sleep(1)

# --- Part 2: The Core Logic (Data Structures & Algorithms) ---
async def monitor_log_file(file_path: Path):
    """
    Monitors a single file using a Sliding Window Algorithm to detect error density.
    """
    print(f"[*] Monitoring active stream: {file_path.name}")
    
    # [DATA STRUCTURE] 'defaultdict(deque)'
    # We use a Deque (Double-Ended Queue) because popping from the
    # start is O(1), whereas a standard list is O(N).
    # Key: The keyword (e.g., "ERROR")
    # Value: A deque of timestamps [10:00:01, 10:00:02, ...]
    keyword_events = defaultdict(deque)

    async for line in tail_file(file_path):
        current_time = time.time()
        
        # Visual feedback (Optional: comment out for silence)
        # print(f"   -> [{file_path.name}] {line}")

        for keyword in KEYWORDS:
            # [ALGORITHM Step 1] Pattern Matching
            if keyword in line:
                # Record the exact time this event happened
                keyword_events[keyword].append(current_time)
                
                # [ALGORITHM Step 2] Prune the Sliding Window
                # We remove any events that happened longer than WINDOW_SIZE_SECONDS ago.
                # Since the queue is chronological, we only check the left (oldest) side.
                while keyword_events[keyword] and current_time - keyword_events[keyword][0] > WINDOW_SIZE_SECONDS:
                    keyword_events[keyword].popleft() # O(1) Operation efficiently removes old data
                
                # [ALGORITHM Step 3] Check Density Threshold
                # If the queue still has >= 3 items, they must all be within the last 10 seconds.
                current_density = len(keyword_events[keyword])
                
                if current_density >= ALERT_THRESHOLD:
                    print(f"\n{'🚨'*5} HIGH TRAFFIC ALERT {'🚨'*5}")
                    print(f"   Source: {file_path.name}")
                    print(f"   Pattern: {current_density} '{keyword}'s detected in {WINDOW_SIZE_SECONDS}s")
                    print(f"{'='*40}\n")
                    
                    # Optional: Clear the window to prevent duplicate alerts for the same burst

# --- Part 3: Orchestration ---
async def run_processor(directory: str):
    dir_path = Path(directory)
    
    # 1. Wait for the directory to exist (Resilience)
    if not dir_path.exists():
        while not dir_path.exists():
            print(f"Waiting for directory '{directory}' to be created...")
            await asyncio.sleep(5)

    print(f"--- Locking onto directory: {dir_path.resolve()} ---")

    # 2. Wait for files to generate (Dynamic Discovery)
    while not list(dir_path.glob("*.log")):
        print("Waiting for log files to appear...")
        await asyncio.sleep(5)

    log_files = list(dir_path.glob("*.log"))
    print(f"Found {len(log_files)} active log services.")

    # 3. Launch Concurrent Tasks
    # We create an independent monitor task for every file found.
    tasks = [monitor_log_file(log) for log in log_files]
    
    # [ASYNC MODEL] Run all file watchers simultaneously
    await asyncio.gather(*tasks)

def main():
    # CLI Argument Parsing
    parser = argparse.ArgumentParser(description="Real-Time Log Processor with Sliding Window Analysis")
    parser.add_argument("directory", type=str, help="Path to log directory")
    args = parser.parse_args()

    try:
        # Windows/Linux compatible asyncio runner
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(run_processor(args.directory))
    except KeyboardInterrupt:
        print("\n--- Monitoring Stopped ---")

if __name__ == "__main__":
    main()