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
        self.output_dir = "time_sync"
        
    def initialize(self, properties):
        """Initialize the module with properties from the configuration."""
        self.module_info("ServerClockSyncPublisherModule initialized")
        
        # Get output directory from properties if specified
        if "outputFilePath" in properties:
            self.output_dir = os.path.dirname(properties["outputFilePath"])
        
        # Create output directory if it doesn't exist
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Note: Date-based files will be created when first data is written
        
        self.module_info(f"Output directory: {self.output_dir}")
        
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
    
    def get_current_output_file(self):
        """Get the current date-based output file path."""
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{current_date}_server_clock_sync_publisher.txt"
        return os.path.join(self.output_dir, filename)
        
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
            
            # Save to log file with date-based filename
            current_output_file = self.get_current_output_file()
            
            # Create file with header if it doesn't exist
            if not os.path.exists(current_output_file):
                with open(current_output_file, 'w') as f:
                    f.write("# Server Clock Sync Publisher Data Log\n")
                    f.write("# Format: Timestamp | Published Clock Sync Message\n")
                    f.write("# " + "="*50 + "\n")
            
            with open(current_output_file, 'a') as f:
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
        annotator.addProperty("outputFilePath", "time_sync/", "Directory to save published clock sync data logs (date-based files)")
        annotator.addProperty("schedule", {
            "periodic": [{
                "period_seconds": 60
            }],
            "timed": []
        }, "Schedule for publishing clock sync messages") 