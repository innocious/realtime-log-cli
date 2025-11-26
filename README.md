# Real-time Log Monitoring System

This project is a two-part solution for analyzing continuous log data, demonstrating real-time monitoring and threshold-based alerting.

1. Log Processor (log_processor.py) - Core Monitoring

The Log Processor is the main application responsible for monitoring service health. It continuously reads new log entries and analyzes them for critical events.

A. Core Functionality

Real-time Tailing: The processor efficiently reads new log lines as they are written, simulating a live data stream.

Time-Windowed Aggregation: This is the core logic. Critical events (ERROR, WARNING) are counted within a specific time window (default: 60 seconds) to identify genuine traffic spikes.

Threshold Alerting: Triggers a HIGH TRAFFIC ALERT if the aggregated count meets or exceeds a defined threshold within the time window.

Dynamic Path: The log directory is specified via a command-line argument, making the script portable across operating systems.

B. Usage

The processor requires the path to the directory containing the log files.

### Example 1: Use the default relative path 'live_logs'
```python log_processor.py```

### Example 2: Specify a custom path (cross-platform compatible)
``` python log_processor.py --path ./my_test_logs```


C. Sample Output (Alert)

🚨🚨🚨🚨🚨 HIGH TRAFFIC ALERT 🚨🚨🚨🚨🚨
    Source: payment_gateway.log
    Pattern: 11 'WARNING's detected in 60s
========================================


2. Log Generator (log_generator.py) - Data Source

The Log Generator is a utility script used to create the log files and simulate the live, randomized data traffic needed for the processor to monitor.

A. Core Functionality

Traffic Simulation: Continuously writes log entries for multiple services at randomized intervals, including sporadic WARNING and ERROR events.

Configurable Output: The output directory for the logs is configurable via a command-line argument to match the processor's monitoring path.

B. Usage

The generator's path must match the path used by the Log Processor.

### Example: Create logs in the 'live_logs' directory
python log_generator.py

