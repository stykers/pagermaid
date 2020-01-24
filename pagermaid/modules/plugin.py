""" PagerMaid module to manage plugins. """

from os import getcwd, remove
from os.path import exists
from shutil import move
from pagermaid.listener import listener
from pagermaid.modules import plugin_list as active_plugins
from pagermaid.modules import __list_plugins


@listener(outgoing=True, command="plugin",
          description="Utility to manage plugins installed to PagerMaid.",
          parameters="{status|install|remove|enable|disable} <plugin name/file>")
async def plugin(context):
    parameters = context.pattern_match.group(1).split(' ')
    reply = await context.get_reply_message()
    if parameters[0] == "install":
        await context.edit("Installing plugin . . .")
        if len(parameters) == 1:
            if reply:
                file_path = await context.client.download_media(
                    reply
                )
            else:
                file_path = await context.download_media()
            if file_path is None or not file_path.endswith('.py'):
                await context.edit("Unable to obtain plugin file from attachments.")
                try:
                    remove(str(file_path))
                except FileNotFoundError:
                    pass
                return
            move(file_path, f"{getcwd()}/plugins/")
            await context.edit("Plugin has been installed, PagerMaid is restarting.")
            await context.client.disconnect()
        else:
            await context.edit("Invalid arguments.")
    if parameters[0] == "remove":
        if len(parameters) == 2:
            if "/" in parameters[1] or not exists(f"{getcwd()}/plugins/{parameters[1]}.py"):
                await context.edit("Invalid plugin.")
            else:
                remove(f"{getcwd()}/plugins/{parameters[1]}.py")
                await context.edit(f"Removed plugin {parameters[1]}, PagerMaid is restarting.")
                await context.client.disconnect()
    if parameters[0] == "status":
        if len(parameters) == 1:
            inactive_plugins = sorted(__list_plugins())
            if not len(inactive_plugins) == 0:
                for target_plugin in active_plugins:
                    inactive_plugins.remove(target_plugin)
            active_plugins_string = ""
            inactive_plugins_string = ""
            for target_plugin in active_plugins:
                active_plugins_string += f"{target_plugin}, "
            active_plugins_string = active_plugins_string[:-2]
            for target_plugin in inactive_plugins:
                inactive_plugins_string += f"{target_plugin}, "
            inactive_plugins_string = inactive_plugins_string[:-2]
            if len(active_plugins) == 0:
                active_plugins_string = "`There are no active plugins.`"
            if len(inactive_plugins) == 0:
                inactive_plugins_string = "`There are no failed plugins.`"
            output = f"**Plugins**\n" \
                     f"Active: {active_plugins_string}\n" \
                     f"Failed: {inactive_plugins_string}"
            await context.edit(output)
    else:
        await context.edit("Invalid arguments.")
