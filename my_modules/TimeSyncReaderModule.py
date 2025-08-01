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
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Extract the actual payload from ChannelData
            if hasattr(data, 'payload') and data.payload:
                # Try to get the actual ClockSyncData content
                try:
                    # For now, just show the raw payload info
                    data_str = f"ClockSyncData payload (size: {len(data.payload) if data.payload else 0})"
                    # You can add specific parsing here if you know the ClockSyncData format
                except Exception as parse_error:
                    data_str = f"Raw payload (size: {len(data.payload) if data.payload else 0})"
            else:
                data_str = "No payload data"
            
            # Print to console
            self.module_info(f"Received ClockSyncData: {data_str}")
            print(f"[TimeSyncReader] {timestamp} | ClockSyncData: {data_str}")
            
            # Save to text file
            with open(self.output_file_path, 'a') as f:
                f.write(f"{timestamp} | {data_str}\n")
            
        except Exception as e:
            error_msg = f"Error processing ClockSyncData: {str(e)}"
            self.module_warning(error_msg)
            print(f"[TimeSyncReader] ERROR: {error_msg}")
            
            # Save error to file
            with open(self.output_file_path, 'a') as f:
                f.write(f"{timestamp} | ERROR: {error_msg}\n")
    
    def annotateModule(self, annotator):
        """Annotate the module for CLAID Designer."""
        annotator.setDisplayName("Time Sync Reader Module")
        annotator.setDescription("Reads and prints ClockSyncData for time syncing")
        
        # Input channels
        annotator.addInputChannel("ClockSyncData", str, "Clock sync data")
        
        # Properties
        annotator.addProperty("outputFilePath", "/Users/robin/Code/mind-wandering_server/time_sync_data.txt", "Path to save time sync data") 