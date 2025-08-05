from claid.module.module import Module
from claid.module.module_annotator import ModuleAnnotator
import time
import os
from datetime import datetime, timedelta

class ServerClockSyncPublisherModule(Module):
    """
    A CLAID module that publishes clock synchronization messages from the server.
    Sends timestamp data to the ClockSyncServerToWatch channel for time synchronization.
    """
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.output_file_path = "server_clock_sync_publisher.txt"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("ServerClockSyncPublisherModule initialized")
        
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
                f.write("# Server Clock Sync Publisher Data Log\n")
                f.write("# Format: Timestamp | Published Clock Sync Message\n")
                f.write("# " + "="*50 + "\n")
        
        self.module_info(f"Output file: {self.output_file_path}")
        
        # Create the output channel for publishing clock sync messages
        self.output_channel = self.publish("ClockSyncServerToWatch", str())
        self.module_info("ServerClockSyncPublisherModule output channel created")
        
        # Register function based on Schedule from properties
        if "schedule" in properties:
            schedule = properties["schedule"]
            # Parse the schedule to get the interval
            interval_seconds = 60  # default
            if "periodic" in schedule and len(schedule["periodic"]) > 0:
                periodic = schedule["periodic"][0]
                if "period_seconds" in periodic:
                    interval_seconds = periodic["period_seconds"]
                elif "period_minutes" in periodic:
                    interval_seconds = periodic["period_minutes"] * 60
                elif "period_milliseconds" in periodic:
                    interval_seconds = periodic["period_milliseconds"] / 1000
            
            self.running = True
            self.register_periodic_function("publish_clock_sync", self.publish_clock_sync, timedelta(seconds=interval_seconds))
            self.module_info(f"ServerClockSyncPublisherModule registered with {interval_seconds}-second interval from schedule")
        else:
            # Fallback to default 60-second interval if no schedule provided
            self.running = True
            self.register_periodic_function("publish_clock_sync", self.publish_clock_sync, timedelta(minutes=1))
            self.module_info("ServerClockSyncPublisherModule using default 60-second interval")
        
    def publish_clock_sync(self):
        """Publish a clock sync message to the ClockSyncServerToWatch channel."""
        if not self.running and "schedule" not in self.properties:
            return
            
        try:
            # Get current timestamp in milliseconds
            current_time = datetime.now()
            timestamp_ms = int(current_time.timestamp() * 1000)
            
            # Create the clock sync message with server timestamp
            clock_sync_message = f"server_publishing_time {timestamp_ms}; "
            
            # Publish the message to the ClockSyncServerToWatch channel
            self.output_channel.post(clock_sync_message)
            
            # Log the published message to console
            self.module_info(f"Published clock sync message: {clock_sync_message}")
            print(f"[ServerClockSyncPublisher] {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | Published: {clock_sync_message}")
            
            # Save to log file
            with open(self.output_file_path, 'a') as f:
                f.write(f"{current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | {clock_sync_message}\n")
            
        except Exception as e:
            self.module_warning(f"Error publishing clock sync message: {str(e)}")
    
    def annotateModule(self, annotator):
        """Annotate the module for CLAID Designer."""
        annotator.setDisplayName("Server Clock Sync Publisher Module")
        annotator.setDescription("Publishes clock synchronization messages from the server to ClockSyncServerToWatch channel")
        
        # Output channels
        annotator.addOutputChannel("ClockSyncServerToWatch", str, "Clock sync messages published from server")
        
        # Properties
        annotator.addProperty("outputFilePath", "server_clock_sync_publisher.txt", "Path to save published clock sync data log")
        annotator.addProperty("schedule", {
            "periodic": [{
                "period_seconds": 60
            }],
            "timed": []
        }, "Schedule for publishing clock sync messages") 