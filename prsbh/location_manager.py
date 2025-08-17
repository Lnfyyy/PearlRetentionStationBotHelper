from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.rtext import RText, RTextList
import os
import json

class LocationManager:
    def __init__(self,server: PluginServerInterface):
        data_folder = server.get_data_folder()
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        self.locations_path = os.path.join(data_folder, 'locations.json')
        self.config_path = os.path.join(data_folder, 'config.json')
        self.locations = {}
        self.config = {"bot_name": "bot_pearl", "item_name": "minecraft:iron_nugget"}
        self.load(server=server)

    def load(self, server: PluginServerInterface):
        if not os.path.exists(self.locations_path):
            self.save()
        with open(self.locations_path, 'r', encoding='utf-8') as f:
            try:
                self.locations = json.load(f)
            except json.JSONDecodeError:
                server.logger.info("§c位置文件加载失败，请检查json文件格式是否正确。")
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        with open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                self.config = json.load(f)
            except json.JSONDecodeError:
                server.logger.info("§c配置文件加载失败，请检查json文件格式是否正确。")
    
    def save(self):
        with open(self.locations_path, 'w', encoding='utf-8') as f:
            json.dump(self.locations, f, indent=4)

    def get_location_list(self):
        loaction_list = []
        for i in self.locations.keys():
            loaction_list.append(RText(f"{i}").h(
                f"§f位置：§a[{self.locations[i]['pos'][0]}, {self.locations[i]['pos'][1]}, {self.locations[i]['pos'][2]}]\n",
                f"§f维度：§e{self.locations[i]['dim']}\n"
                f"§f方向：§b{self.locations[i]['facing']}")
            )
        return loaction_list