from mcdreforged.api.all import *

from .help import prs_help
from .location_manager import LocationManager
from .search import search_mixed
from math import floor
import time
from collections import OrderedDict

import minecraft_data_api as mdapi

def register_commands(server, location_manager: LocationManager):
    server.register_command(
        Literal("!!prs").then(
            Literal("list").runs(lambda src: prs_list(src, location_manager))
        ).then(
            Literal("add").then(
                Text("name").runs(lambda src, ctx: prs_add(src, ctx["name"], location_manager))
            )
        ).then(
            Literal("remove").then(
                Text("name").runs(lambda src, ctx: prs_remove(src, ctx["name"], location_manager))
            )
        ).then(
            Literal("reload").requires(lambda src: src.has_permission(3)).runs(lambda src: prs_reload(src, location_manager))
        ).then(
            Text("name").runs(lambda src, ctx: prs_search(src, ctx["name"], location_manager, server))
        ).runs(lambda src: prs_help(src))
    )

def prs_list(source: CommandSource, location_manager: LocationManager):
    rtext_list = RTextList()
    loaction_list = location_manager.get_location_list()
    rtext_list.append(RText("\n"))
    rtext_list.append(RText("--------------------\n"))
    for i in loaction_list:
        rtext_list.append(i)
        rtext_list.append(RText(" "))
        rtext_list.append(RText("§b[前往]").c(RAction.suggest_command, f"!!prs {i}").h(f"§f准备前往 §e{i}"))
        rtext_list.append(RText(" "))
        rtext_list.append(RText("§c[删除]").c(RAction.suggest_command, f"!!prs remove {i}").h(f"§f删除 §e{i}"))
        rtext_list.append(RText("\n"))
    rtext_list.append(RText("--------------------"))
    source.reply(rtext_list)

@new_thread("PRSAddThread")
def prs_add(source: CommandSource, name: str, location_manager: LocationManager):
    if not isinstance(source, PlayerCommandSource):
        source.reply("你必须是个玩家才可以添加位置")
        return
    player_name = source.player
    pos = mdapi.get_player_info(player_name, "Pos")
    pos_cal = []
    dim = mdapi.get_player_info(player_name, "Dimension")
    facing = mdapi.get_player_info(player_name, "Rotation")
    if not (round(pos[0]-floor(pos[0]),3)==0.238 or round(pos[0]-floor(pos[0]),3)==0.762 or round(pos[2]-floor(pos[2]),3)==0.238 or round(pos[2]-floor(pos[2]),3)==0.762):
        source.reply("§c添加失败，请确保顶着箱子并面向箱子")
        return
    #北
    if facing[0]>=135 and facing[0]<225:
        pos_cal = [floor(pos[0])+0.5, floor(pos[1]), floor(pos[2])+0.238]
        facing_cal = [180, 0]
    #东
    elif facing[0]>=-135 and facing[0]<-45:
        pos_cal = [floor(pos[0])+0.762, floor(pos[1]), floor(pos[2])+0.5]
        facing_cal = [-90, 0]
    #南
    elif facing[0]>=-45 and facing[0]<45:
        pos_cal = [floor(pos[0])+0.5, floor(pos[1]), floor(pos[2])+0.762]
        facing_cal = [0, 0]
    #西
    else:
        pos_cal = [floor(pos[0])+0.238, floor(pos[1]), floor(pos[2])+0.5]
        facing_cal = [90, 0]
    location_manager.locations[name] = {"pos": pos_cal, "facing": facing_cal, "dim": dim}
    location_manager.save()
    source.reply(f"§a已添加 §f{name} §a{pos_cal} §b{facing_cal} §e{dim}")

def prs_remove(source: CommandSource, name: str, location_manager: LocationManager):
    if name not in location_manager.locations:
        source.reply(f"§c{name} §c不存在")
        return
    location_manager.locations.pop(name, None)
    location_manager.save()
    source.reply(f"§a已删除 §f{name}")

def prs_search(source: CommandSource, name: str, location_manager: LocationManager, server):
    if name not in location_manager.locations:
        search_result = search_mixed(location_manager.locations.keys(), name, 50)
        if len(search_result) == 0:
            source.reply(f"§c未找到 §f{name} §c的位置")
            return
        rtext_list = RTextList()
        rtext_list.append(RText("\n"))
        rtext_list.append(RText("§b搜索到以下位置："))
        for i in search_result:
            rtext_list.append(RText("\n"))
            rtext_list.append(RText(f"{i[0]} ").h(
                f"§f位置：§a[{location_manager.locations[i[0]]['pos'][0]}, {location_manager.locations[i[0]]['pos'][1]}, {location_manager.locations[i[0]]['pos'][2]}]\n",
                f"§f维度：§e{location_manager.locations[i[0]]['dim']}\n"
                f"§f方向：§b{location_manager.locations[i[0]]['facing']}"
            ))
            rtext_list.append(RText(f"§e匹配度{i[1]}% "))
            rtext_list.append(RText("§b[前往]").c(RAction.suggest_command, f"!!prs {i[0]}").h(f"§f准备前往 §e{i[0]}"))
        source.reply(rtext_list)
    else:
        prs_goto(source, name, location_manager, server)

@new_thread("PRSGotoThread")
def prs_goto(source: CommandSource, name: str, location_manager: LocationManager, server: ServerInterface):
    player_list = mdapi.get_server_player_list()
    try:
        if location_manager.config['bot_name'] in player_list.players:
            rtext_list = RTextList()
            rtext_list.append(RText(f"§c{location_manager.config['bot_name']} 已在线，请先把他踢出游戏 "))
            command = f"/player {location_manager.config['bot_name']} kill"
            rtext_list.append(RText("§b[一键踢出]").c(RAction.run_command, command).h(command))
            source.reply(rtext_list)
            return
    except Exception as e:
        source.reply(f"读取玩家列表失败{e}")

    server.execute(f"/player {location_manager.config['bot_name']} spawn at {location_manager.locations[name]['pos'][0]} {location_manager.locations[name]['pos'][1]} {location_manager.locations[name]['pos'][2]} facing {location_manager.locations[name]['facing'][0]} {location_manager.locations[name]['facing'][1]} in {location_manager.locations[name]['dim']}")
    while True:
        player_list = mdapi.get_server_player_list()
        if location_manager.config['bot_name'] in player_list.players:
            prsbh_inventory = mdapi.get_player_info(location_manager.config['bot_name'],"Inventory")
            break
        time.sleep(1)

    prsbh_inventory_result = []
    for item in prsbh_inventory:
        id = item.get("id", "Unknown")
        custom_name = None        
        slot = item.get("Slot", "Unknown")
        if "components" in item and isinstance(item["components"], (dict, OrderedDict)):
            custom_name = item["components"].get("minecraft:custom_name",None)
        
        prsbh_inventory_result.append({
        "slot" : slot,
        "id" : id,
        "custom_name" : custom_name
        })
    for item_data in prsbh_inventory_result:
        print(f"{item_data["slot"]} | {item_data["id"]} | {item_data["custom_name"] or "-default"}")
        
        




    
def prs_reload(source: CommandSource, location_manager: LocationManager):
    location_manager.load(server=source.get_server)
    source.reply("重载配置文件成功")