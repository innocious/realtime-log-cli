# Real-time Log Monitoring System

This project is a solution for analyzing continuous log data, demonstrating real-time monitoring and threshold-based alerting.

### Log Processor (real_time_log_processor.py) - Core Monitoring Functionality

The Log Processor is the main application responsible for monitoring service health. It continuously reads new log entries and analyzes them for critical events.

1. Core Functionality

Real-time Tailing: The processor efficiently reads new log lines as they are written, simulating a live data stream.

Time-Windowed Aggregation: This is the core logic. Critical events (ERROR, WARNING) are counted within a specific time window (default: 60 seconds) to identify genuine traffic spikes.

Threshold Alerting: Triggers a HIGH TRAFFIC ALERT if the aggregated count meets or exceeds a defined threshold within the time window.

Dynamic Path: The log directory is specified via a command-line argument, making the script portable across operating systems.

B. Usage

The processor requires the path to the directory containing the log files.

### Example 1: Use the default relative path 'live_logs'
```python real_time_log_processor.py live_logs```

### Example 2: Specify a custom path (cross-platform compatible)
` python real_time_log_processor.py --path /Users/user/projects/live_logs2 `


C. Sample Output (Alert)

🚨🚨🚨🚨🚨 HIGH TRAFFIC ALERT 🚨🚨🚨🚨🚨
    Source: payment_gateway.log
    Pattern: 11 'WARNING's detected in 60s
========================================




| Time Windows (s) | Alert Threshold -3 | Alert Threshold -10 |
|:----------------:|:------------------:|:-------------------:|
| 15               | 22                 | 0                   |
| 30               | 24                 | 0                   |
| 60               | 28                 | 20                  |
| 120              | 42                 | 24                  |
| 180              | 54                 | 30                  |