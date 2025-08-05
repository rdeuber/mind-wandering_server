from claid import CLAID
from claid.module.module_factory import ModuleFactory
from my_modules.ServerClockSyncSubscriberModule import ServerClockSyncSubscriberModule
from my_modules.ServerClockSyncPublisherModule import ServerClockSyncPublisherModule

module_factory = ModuleFactory()
module_factory.register_default_modules()

# Register custom modules.
module_factory.register_module(ServerClockSyncSubscriberModule)
module_factory.register_module(ServerClockSyncPublisherModule)

CLAID_instance = CLAID()
CLAID_instance.start(
    "CLAIDConfig.json", # config_path: Path to the CLAID configuration file.
    "Server", # hostname: Name of the host to execute.
    "the_server_user", # user_id: User name of the server.
    "the_server_device", # device_id: Device name of the server.
    module_factory = module_factory, # module_factory: Module factory to register custom modules.
)