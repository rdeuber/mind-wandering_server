from claid.module.module import Module
from claid.module.module_annotator import ModuleAnnotator
import time
import os
from datetime import datetime, timedelta

class ServerClockSyncModule(Module):
    """
    A CLAID module that posts clock sync messages every minute from the server.
    Used for server-side time synchronization.
    """
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.output_file_path = "/Users/robin/Code/mind-wandering_server/server_clock_sync_data.txt"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("ServerClockSyncModule initialized")
        
        # Get output file path from properties if specified
        if "outputFilePath" in properties:
            self.output_file_path = properties["outputFilePath"]
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the output file if it doesn't exist
        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, 'w') as f:
                f.write("# Server Clock Sync Data Log\n")
                f.write("# Format: Timestamp | Server Clock Sync Message\n")
                f.write("# " + "="*50 + "\n")
        
        self.module_info(f"Output file: {self.output_file_path}")
        
        # Start the clock sync loop - schedule it to run every 60 seconds
        self.running = True
        self.register_periodic_function("post_clock_sync", self.post_clock_sync, timedelta(minutes=1))  # Every 60 seconds
        
        self.module_info("ServerClockSyncModule scheduled periodic clock sync messages")

        self.output_channel = self.publish("ServerClockSyncData", str())
        self.module_info("ServerClockSyncModule output channel created")

        
    def post_clock_sync(self):
        """Post a clock sync message to the channel."""
        if not self.running:
            return
            
        try:
            # Get current timestamp
            current_time = datetime.now()
            timestamp_ms = int(current_time.timestamp() * 1000)
            
            # Create the clock sync message
            clock_sync_message = f"SERVER CLOCK SYNC: Server performing clock synchronization at {timestamp_ms} ms"
            
            # Post the message to the ServerClockSyncData channel
            # In CLAID, we use the publish method to send data to output channels
            self.output_channel.post(clock_sync_message)
            
            # Log the message to console
            self.module_info(f"Posted clock sync message: {clock_sync_message}")
            print(f"[ServerClockSync] {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | Posted: {clock_sync_message}")
            
            # Save to text file
            with open(self.output_file_path, 'a') as f:
                f.write(f"{current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | {clock_sync_message}\n")
            
        except Exception as e:
            self.module_warning(f"Error posting clock sync message: {str(e)}")
    
    def annotateModule(self, annotator):
        """Annotate the module for CLAID Designer."""
        annotator.setDisplayName("Server Clock Sync Module")
        annotator.setDescription("Posts clock sync messages every minute from the server")
        
        # Output channels
        annotator.addOutputChannel("ServerClockSyncData", str, "Clock sync messages from server")
        
        # Properties
        annotator.addProperty("outputFilePath", "/Users/robin/Code/mind-wandering_server/server_clock_sync_data.txt", "Path to save server clock sync data") 