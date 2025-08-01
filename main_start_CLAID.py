from claid import CLAID
from claid.module.module_factory import ModuleFactory
from my_modules.TimeSyncReaderModule import TimeSyncReaderModule

module_factory = ModuleFactory()
module_factory.register_default_modules()

# Register custom modules.
module_factory.register_module(TimeSyncReaderModule)

CLAID_instance = CLAID()
CLAID_instance.start(
    "CLAIDConfig.json", # config_path: Path to the CLAID configuration file, you will need to create this in Section 2.
    "Server", # hostname: Name of the host to execute. Needs to match with the "hostname" in the CLAID configuration.
    "the_server_user", # user_id: User name of the server. Can be any string.
    "the_server_device", # device_id: Device name of the server. Can be any string.
    module_factory = module_factory, # module_factory: Module factory to register custom modules.
)