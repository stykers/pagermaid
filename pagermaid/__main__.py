""" PagerMaid launch sequence. """

from sys import path
from importlib import import_module
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from pagermaid import bot, logs, working_dir
from pagermaid.modules import module_list, plugin_list
try:
    from pagermaid.interface import server
except TypeError:
    logs.error("Web interface is configured to bind to an invalid address.")
    server = None
except KeyError:
    logs.error("Web interface configuration is missing in the config file.")
    server = None


path.insert(1, f"{working_dir}/plugins")

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
    except BaseException as exception:
        logs.info(f"Error loading plugin {plugin_name}: {exception}")
        plugin_list.remove(plugin_name)
if server is not None:
    import_module("pagermaid.interface")
logs.info("PagerMaid have started, type -help in any chat for help message.")
bot.run_until_disconnected()
if server is not None:
    server.stop()
