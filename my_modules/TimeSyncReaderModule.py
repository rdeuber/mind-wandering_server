from claid.module.module import Module
from claid.module.module_annotator import ModuleAnnotator
import os
from datetime import datetime

class TimeSyncReaderModule(Module):
    """
    A simple CLAID module that reads ClockSyncData and prints it.
    Used for time syncing and data monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.clock_sync_channel = None
        self.output_file_path = "/Users/robin/Code/mind-wandering_server/time_sync_data.txt"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("TimeSyncReaderModule initialized")
        
        # Get output file path from properties if specified
        if "outputFilePath" in properties:
            self.output_file_path = properties["outputFilePath"]
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the output file if it doesn't exist
        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, 'w') as f:
                f.write("# Time Sync Data Log\n")
                f.write("# Format: Timestamp | ClockSyncData\n")
                f.write("# " + "="*50 + "\n")
        
        # Subscribe to the ClockSyncData channel
        self.clock_sync_channel = self.subscribe("ClockSyncData", "", self.on_clock_sync)
        
        self.module_info(f"TimeSyncReaderModule subscribed to ClockSyncData channel")
        self.module_info(f"Output file: {self.output_file_path}")
    
    def on_clock_sync(self, data):
        """Handle incoming ClockSyncData and print it."""
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
            self.module_info(f"Received ClockSyncData: {clock_sync_data}")
            print(f"[TimeSyncReader] Local: {local_timestamp} | Original: {original_timestamp} | ClockSyncData: {clock_sync_data}")
            
            # Save to text file
            with open(self.output_file_path, 'a') as f:
                f.write(f"Local: {local_timestamp} | Original: {original_timestamp} | {clock_sync_data}\n")
            
        except Exception as e:
            self.module_warning(f"Error processing ClockSyncData: {str(e)}")
    
    def annotateModule(self, annotator):
        """Annotate the module for CLAID Designer."""
        annotator.setDisplayName("Time Sync Reader Module")
        annotator.setDescription("Reads and prints ClockSyncData for time syncing")
        
        # Input channels
        annotator.addInputChannel("ClockSyncData", str, "Clock sync data")
        
        # Properties
        annotator.addProperty("outputFilePath", "/Users/robin/Code/mind-wandering_server/time_sync_data.txt", "Path to save time sync data") 