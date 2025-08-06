from claid.module.module import Module
from claid.module.module_annotator import ModuleAnnotator
import os
import csv
from datetime import datetime

class ServerClockSyncSubscriberModule(Module):
    """
    A CLAID module that receives and analyzes clock synchronization messages from the watch.
    Parses timing data, calculates latency and clock offset between server and watch devices.
    """
    
    def __init__(self):
        super().__init__()
        self.clock_sync_channel = None
        self.output_file_path = "server_clock_sync_subscriber.txt"
        self.csv_file_path = "server_clock_sync_subscriber.csv"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("ServerClockSyncSubscriberModule initialized")
        
        # Get output file path from properties if specified
        if "outputFilePath" in properties:
            self.output_file_path = properties["outputFilePath"]
            # Generate CSV file path based on the text file path
            base_path = os.path.splitext(self.output_file_path)[0]
            self.csv_file_path = f"{base_path}.csv"
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file_path)
        if output_dir:  # Only create directory if there's a directory path
            os.makedirs(output_dir, exist_ok=True)
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'server_receiving_time_formatted',
                    'server_receiving_time_ms',
                    'message_timestamp', 
                    'server_publishing_time',
                    'watch_receiving_time',
                    'watch_publishing_time',
                    'estimated_latency_ms',
                    'time_difference_ms',
                    'raw_clock_sync_data'
                ])
        
        # Create the output file if it doesn't exist
        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, 'w') as f:
                f.write("# Server Clock Sync Subscriber Data Log\n")
                f.write("# Format: Server Receiving Time | Message Timestamp | Clock Sync Data | Server Receiving Time\n")
                f.write("# Parsed times and calculated latency/offset are included below each entry\n")
                f.write("# " + "="*70 + "\n")
        
        # Subscribe to the ClockSyncWatchToServer channel
        self.clock_sync_channel = self.subscribe("ClockSyncWatchToServer", "", self.on_clock_sync)
        
        self.module_info(f"ServerClockSyncSubscriberModule subscribed to ClockSyncWatchToServer channel")
        self.module_info(f"Text output file: {self.output_file_path}")
        self.module_info(f"CSV output file: {self.csv_file_path}")
    
    def on_clock_sync(self, data):
        """Handle incoming clock sync messages, parse timing data, and calculate latency/offset."""
        try:
            # Get current local timestamp in milliseconds
            server_receiving_time = int(datetime.now().timestamp() * 1000)
            
            # Get message timestamp if available
            message_timestamp = "Unknown"
            if hasattr(data, 'timestamp') and data.timestamp:
                message_timestamp = data.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Extract the actual data from ChannelData
            if hasattr(data, 'data') and data.data:
                clock_sync_data = data.data
            else:
                clock_sync_data = "No clock sync data found"
            
            # Parse the clock sync data to extract times as integers
            server_publishing_time = None
            watch_receiving_time = None
            watch_publishing_time = None
            
            if isinstance(clock_sync_data, str):
                # Parse the message format: "server_publishing_time 1754371911816; watch_receiving_time 1754371911061; watch_publishing_time 1754371911063;"
                parts = clock_sync_data.split(';')
                for part in parts:
                    part = part.strip()
                    if part.startswith('server_publishing_time '):
                        try:
                            server_publishing_time = int(part.split(' ')[1])
                        except (IndexError, ValueError):
                            pass
                    elif part.startswith('watch_receiving_time '):
                        try:
                            watch_receiving_time = int(part.split(' ')[1])
                        except (IndexError, ValueError):
                            pass
                    elif part.startswith('watch_publishing_time '):
                        try:
                            watch_publishing_time = int(part.split(' ')[1])
                        except (IndexError, ValueError):
                            pass
            
            # Calculate estimated latency
            estimated_latency = None
            if server_publishing_time is not None and server_receiving_time is not None:
                estimated_latency = (server_receiving_time - server_publishing_time) / 2
            
            # Calculate time difference between devices (clock offset)
            time_difference = None
            if server_publishing_time is not None and watch_receiving_time is not None and estimated_latency is not None:
                # Time difference = (watch_receiving_time - server_publishing_time) - latency
                # This gives us the clock offset between devices
                time_difference = (watch_receiving_time - server_publishing_time) - estimated_latency
            
            # Print to console
            self.module_info(f"Received clock sync message: {clock_sync_data}")
            print(f"[ServerClockSyncSubscriber] Server receiving: {server_receiving_time} | Message: {message_timestamp} | Clock sync data: {clock_sync_data}")
            if server_publishing_time is not None:
                print(f"  Parsed times - Server publishing: {server_publishing_time}, Watch receiving: {watch_receiving_time}, Watch publishing: {watch_publishing_time}")
                if estimated_latency is not None:
                    print(f"  Estimated latency: {estimated_latency:.2f} ms")
                if time_difference is not None:
                    print(f"  Time difference (clock offset): {time_difference:.2f} ms")
            
            # Save to text file
            with open(self.output_file_path, 'a') as f:
                f.write(f"Server receiving: {server_receiving_time} | Message: {message_timestamp} | {clock_sync_data}server_receiving_time {server_receiving_time}\n")
                if server_publishing_time is not None:
                    f.write(f"  Parsed times - Server publishing: {server_publishing_time}, Watch receiving: {watch_receiving_time}, Watch publishing: {watch_publishing_time}\n")
                    if estimated_latency is not None:
                        f.write(f"  Estimated latency: {estimated_latency:.2f} ms\n")
                    if time_difference is not None:
                        f.write(f"  Time difference (clock offset): {time_difference:.2f} ms\n")
            
            # Save to CSV file for machine-readable format
            with open(self.csv_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    datetime.fromtimestamp(server_receiving_time / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    server_receiving_time,
                    message_timestamp,
                    server_publishing_time if server_publishing_time is not None else '',
                    watch_receiving_time if watch_receiving_time is not None else '',
                    watch_publishing_time if watch_publishing_time is not None else '',
                    f"{estimated_latency:.2f}" if estimated_latency is not None else '',
                    f"{time_difference:.2f}" if time_difference is not None else '',
                    clock_sync_data
                ])
            
        except Exception as e:
            self.module_warning(f"Error processing clock sync message: {str(e)}")
    
    def annotateModule(self, annotator):
        """Annotate the module for CLAID Designer."""
        annotator.setDisplayName("Server Clock Sync Subscriber Module")
        annotator.setDescription("Receives and analyzes clock synchronization messages from the watch, calculates latency and clock offset")
        
        # Input channels
        annotator.addInputChannel("ClockSyncWatchToServer", str, "Clock synchronization messages from watch")
        
        # Properties
        annotator.addProperty("outputFilePath", "server_clock_sync_subscriber.txt", "Path to save clock sync analysis data") 