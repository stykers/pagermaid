""" PagerMaid launch sequence. """

from sys import path
from os import getcwd
from importlib import import_module
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from pagermaid import bot, logs
from pagermaid.modules import module_list, plugin_list

path.insert(1, f"{getcwd()}/plugins")

try:
    bot.start()
except PhoneNumberInvalidError:
    print('The phone number entered is invalid. Please make sure to append country code.')
    exit(1)
for module_name in module_list:
    try:
        import_module("pagermaid.modules." + module_name)
    except BaseException:
        logs.info(f"Error loading module {module_name}.")
for plugin_name in plugin_list:
    try:
        import_module("plugins." + plugin_name)
    except BaseException:
        logs.info(f"Error loading plugin {plugin_name}.")
logs.info("PagerMaid have started, The prefix is -, type -help for help message.")
bot.run_until_disconnected()
