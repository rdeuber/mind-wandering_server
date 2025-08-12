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
        self.output_dir = "time_sync"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("ServerClockSyncSubscriberModule initialized")
        
        # Get output directory from properties if specified
        if "outputFilePath" in properties:
            self.output_dir = os.path.dirname(properties["outputFilePath"])
        
        # Create output directory if it doesn't exist
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Note: Date-based files will be created when first data is written
        
        # Subscribe to the ClockSyncWatchToServer channel
        self.clock_sync_channel = self.subscribe("ClockSyncWatchToServer", "", self.on_clock_sync)
        
        self.module_info(f"ServerClockSyncSubscriberModule subscribed to ClockSyncWatchToServer channel")
        self.module_info(f"Output directory: {self.output_dir}")
    
    def get_current_output_files(self):
        """Get the current date-based output file paths."""
        current_date = datetime.now().strftime("%Y%m%d")
        txt_filename = f"{current_date}_server_clock_sync_subscriber.txt"
        csv_filename = f"{current_date}_server_clock_sync_subscriber.csv"
        return os.path.join(self.output_dir, txt_filename), os.path.join(self.output_dir, csv_filename)
    
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
            
            # Save to text file with date-based filename
            current_txt_file, current_csv_file = self.get_current_output_files()
            
            # Create text file with header if it doesn't exist
            if not os.path.exists(current_txt_file):
                with open(current_txt_file, 'w') as f:
                    f.write("# Server Clock Sync Subscriber Data Log\n")
                    f.write("# Format: Server Receiving Time | Message Timestamp | Clock Sync Data | Server Receiving Time\n")
                    f.write("# Parsed times and calculated latency/offset are included below each entry\n")
                    f.write("# " + "="*70 + "\n")
            
            with open(current_txt_file, 'a') as f:
                f.write(f"Server receiving: {server_receiving_time} | Message: {message_timestamp} | {clock_sync_data}server_receiving_time {server_receiving_time}\n")
                if server_publishing_time is not None:
                    f.write(f"  Parsed times - Server publishing: {server_publishing_time}, Watch receiving: {watch_receiving_time}, Watch publishing: {watch_publishing_time}\n")
                    if estimated_latency is not None:
                        f.write(f"  Estimated latency: {estimated_latency:.2f} ms\n")
                    if time_difference is not None:
                        f.write(f"  Time difference (clock offset): {time_difference:.2f} ms\n")
            
            # Create CSV file with header if it doesn't exist
            if not os.path.exists(current_csv_file):
                with open(current_csv_file, 'w', newline='') as csvfile:
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
            
            # Save to CSV file for machine-readable format
            with open(current_csv_file, 'a', newline='') as csvfile:
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
        annotator.addProperty("outputFilePath", "time_sync/", "Directory to save clock sync analysis data (date-based files)") 