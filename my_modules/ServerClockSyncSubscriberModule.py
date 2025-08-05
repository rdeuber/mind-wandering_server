from claid.module.module import Module
from claid.module.module_annotator import ModuleAnnotator
import os
from datetime import datetime

class ServerClockSyncSubscriberModule(Module):
    """
    A simple CLAID module that reads ClockSyncWatchToServer and prints it.
    Used for time syncing and data monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.clock_sync_channel = None
        self.output_file_path = "server_clock_sync_subscriber.txt"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("ServerClockSyncSubscriberModule initialized")
        
        # Get output file path from properties if specified
        if "outputFilePath" in properties:
            self.output_file_path = properties["outputFilePath"]
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file_path)
        if output_dir:  # Only create directory if there's a directory path
            os.makedirs(output_dir, exist_ok=True)
        
        # Create the output file if it doesn't exist
        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, 'w') as f:
                f.write("# Time Sync Data Log\n")
                f.write("# Format: Timestamp | ClockSyncWatchToServer\n")
                f.write("# " + "="*50 + "\n")
        
        # Subscribe to the ClockSyncWatchToServer channel
        self.clock_sync_channel = self.subscribe("ClockSyncWatchToServer", "", self.on_clock_sync)
        
        self.module_info(f"ServerClockSyncSubscriberModule subscribed to ClockSyncWatchToServer channel")
        self.module_info(f"Output file: {self.output_file_path}")
    
    def on_clock_sync(self, data):
        """Handle incoming ClockSyncWatchToServer and print it."""
        try:
            # Get current local timestamp
            local_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Get original message timestamp if available
            original_timestamp = "Unknown"
            if hasattr(data, 'timestamp') and data.timestamp:
                original_timestamp = data.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Extract the actual data from ChannelData
            if hasattr(data, 'data') and data.data:
                clock_sync_data = data.data
            else:
                clock_sync_data = "No clock sync data found"
            
            # Print to console
            self.module_info(f"Received ClockSyncWatchToServer: {clock_sync_data}")
            print(f"[ServerClockSyncSubscriber] Local: {local_timestamp} | Original: {original_timestamp} | ClockSyncWatchToServer: {clock_sync_data}")
            
            # Save to text file
            with open(self.output_file_path, 'a') as f:
                f.write(f"Local: {local_timestamp} | Original: {original_timestamp} | {clock_sync_data}\n")
            
        except Exception as e:
            self.module_warning(f"Error processing ClockSyncWatchToServer: {str(e)}")
    
    def annotateModule(self, annotator):
        """Annotate the module for CLAID Designer."""
        annotator.setDisplayName("Time Sync Reader Module")
        annotator.setDescription("Reads and prints ClockSyncWatchToServer for time syncing")
        
        # Input channels
        annotator.addInputChannel("ClockSyncWatchToServer", str, "Clock sync data")
        
        # Properties
        annotator.addProperty("outputFilePath", "server_clock_sync_subscriber.txt", "Path to save time sync data") 