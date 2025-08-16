from mcdreforged.api.types import *
from .command import register_commands
from .location_manager import LocationManager

def on_load(server: PluginServerInterface, old):
    location_manager = LocationManager(server)
    register_commands(server, location_manager)
    server.register_help_message("!!prs", "珍珠滞留站假人帮手相关指令")
    server.logger.info("§a插件加载成功")