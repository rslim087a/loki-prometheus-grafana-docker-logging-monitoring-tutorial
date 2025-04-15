import json
import time
import os
import sys
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# Create metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'status', 'path'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration in seconds', ['method', 'path'])
http_response_size_bytes = Counter('http_response_size_bytes', 'HTTP response size in bytes', ['method', 'path'])
http_status_codes = Counter('http_status_codes', 'HTTP Status Codes', ['status'])

# Path to the log file
LOG_FILE = '/var/log/generated-logs.txt'

# Initialize last position
last_position = 0

def parse_log_line(line):
    try:
        data = json.loads(line.strip())
        # Extract relevant information
        method = data.get('method', 'UNKNOWN')
        status = str(data.get('status', '0'))
        path = data.get('request', '/unknown')
        bytes_sent = int(data.get('bytes', 0))
        
        # Increment metrics
        http_requests_total.labels(method=method, status=status, path=path).inc()
        http_response_size_bytes.labels(method=method, path=path).inc(bytes_sent)
        http_status_codes.labels(status=status).inc()
        
        # Simulate duration based on response size (just for demo purposes)
        duration = max(0.001, min(bytes_sent / 1000000.0, 10.0))  # Between 1ms and 10s
        http_request_duration_seconds.labels(method=method, path=path).observe(duration)
        
        print(f"Processed log: {method} {path} {status} {bytes_sent}B")
        
    except json.JSONDecodeError:
        print(f"Failed to parse log line: {line}", file=sys.stderr)
    except Exception as e:
        print(f"Error processing log line: {str(e)}", file=sys.stderr)

def tail_log_file():
    global last_position
    
    try:
        if not os.path.exists(LOG_FILE):
            print(f"Waiting for log file {LOG_FILE} to be created...")
            time.sleep(1)
            return
        
        with open(LOG_FILE, 'r') as f:
            # Get file size
            f.seek(0, 2)
            file_size = f.tell()
            
            # If file has been truncated or overwritten, reset position
            if last_position > file_size:
                print("Log file was truncated, resetting position")
                last_position = 0
                
            # If there's new content
            if file_size > last_position:
                # Go to the last read position
                f.seek(last_position)
                
                # Read new lines
                new_lines = f.readlines()
                
                # Process each new line
                for line in new_lines:
                    if line.strip():
                        parse_log_line(line)
                
                # Update position
                last_position = file_size
    except Exception as e:
        print(f"Error in tail_log_file: {str(e)}", file=sys.stderr)
        time.sleep(1)

if __name__ == '__main__':
    print("Starting metrics exporter...")
    
    # Start up the server to expose the metrics
    start_http_server(8082)
    print("Metrics server started on port 8082")
    
    # Main loop
    while True:
        tail_log_file()
        time.sleep(0.1)  # Check for new logs frequently