from mcdreforged.api.types import CommandSource
def prs_help(source: CommandSource):
    help='''
§b珍珠滞留站假人帮手
§e小帅侠a 制作
§f命令帮助信息列表
§7!!prs: §f显示命令帮助信息
§7!!prs reload: §f重载配置文件
§7!!prs list: §f显示所有地点
§7!!prs add <地点名>: §f在当前位置添加一个地点(站在滞留站物品输入口前(箱子前)，并面向箱子)
§7!!prs remove <地点名>: §f删除一个地点
§7!!prs <地点名>: §f搜索地点或者准备前往一个地点'''
    source.reply(help)