""" PagerMaid module to manage plugins. """

from os import getcwd, remove, rename, chdir, path
from os.path import exists
from shutil import move, copyfile
from glob import glob
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import upload_attachment
from pagermaid.modules import plugin_list as active_plugins
from pagermaid.modules import __list_plugins


@listener(outgoing=True, command="plugin", diagnostics=False,
          description="Utility to manage plugins installed to PagerMaid.",
          parameters="{status|install|remove|enable|disable|upload} <plugin name/file>")
async def plugin(context):
    parameters = context.pattern_match.group(1).split(' ')
    reply = await context.get_reply_message()
    plugin_directory = f"{getcwd()}/plugins/"
    if parameters[0] == "install":
        if len(parameters) == 1:
            await context.edit("Installing plugin . . .")
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
            move(file_path, plugin_directory)
            await context.edit(f"Plugin {path.basename(file_path)[:-3]} has been installed, PagerMaid is restarting.")
            await log(f"Installed plugin {path.basename(file_path)[:-3]}.")
            await context.client.disconnect()
        else:
            await context.edit("Invalid arguments.")
    elif parameters[0] == "remove":
        if len(parameters) == 2:
            if exists(f"{plugin_directory}{parameters[1]}.py"):
                remove(f"{plugin_directory}{parameters[1]}.py")
                await context.edit(f"Removed plugin {parameters[1]}, PagerMaid is restarting.")
                await log(f"Removed plugin {parameters[1]}.")
                await context.client.disconnect()
            elif exists(f"{plugin_directory}{parameters[1]}.py.disabled"):
                remove(f"{plugin_directory}{parameters[1]}.py.disabled")
                await context.edit(f"Removed plugin {parameters[1]}.")
                await log(f"Removed plugin {parameters[1]}.")
            elif "/" in parameters[1]:
                await context.edit("Invalid arguments.")
            else:
                await context.edit("The plugin specified does not exist.")
        else:
            await context.edit("Invalid arguments.")
    elif parameters[0] == "status":
        if len(parameters) == 1:
            inactive_plugins = sorted(__list_plugins())
            disabled_plugins = []
            if not len(inactive_plugins) == 0:
                for target_plugin in active_plugins:
                    inactive_plugins.remove(target_plugin)
            chdir("plugins/")
            for target_plugin in glob(f"*.py.disabled"):
                disabled_plugins += [f"{target_plugin[:-12]}"]
            chdir("../")
            active_plugins_string = ""
            inactive_plugins_string = ""
            disabled_plugins_string = ""
            for target_plugin in active_plugins:
                active_plugins_string += f"{target_plugin}, "
            active_plugins_string = active_plugins_string[:-2]
            for target_plugin in inactive_plugins:
                inactive_plugins_string += f"{target_plugin}, "
            inactive_plugins_string = inactive_plugins_string[:-2]
            for target_plugin in disabled_plugins:
                disabled_plugins_string += f"{target_plugin}, "
            disabled_plugins_string = disabled_plugins_string[:-2]
            if len(active_plugins) == 0:
                active_plugins_string = "`There are no active plugins.`"
            if len(inactive_plugins) == 0:
                inactive_plugins_string = "`There are no failed plugins.`"
            if len(disabled_plugins) == 0:
                disabled_plugins_string = "`There are no disabled plugins.`"
            output = f"**Plugins**\n" \
                     f"Active: {active_plugins_string}\n" \
                     f"Disabled: {disabled_plugins_string}\n" \
                     f"Failed: {inactive_plugins_string}"
            await context.edit(output)
        else:
            await context.edit("Invalid arguments.")
    elif parameters[0] == "enable":
        if len(parameters) == 2:
            if exists(f"{plugin_directory}{parameters[1]}.py.disabled"):
                rename(f"{plugin_directory}{parameters[1]}.py.disabled", f"{plugin_directory}{parameters[1]}.py")
                await context.edit(f"Plugin {parameters[1]} have been enabled, PagerMaid is restarting.")
                await log(f"Enabled plugin {parameters[1]}.")
                await context.client.disconnect()
            else:
                await context.edit("The plugin specified does not exist.")
        else:
            await context.edit("Invalid arguments.")
    elif parameters[0] == "disable":
        if len(parameters) == 2:
            if exists(f"{plugin_directory}{parameters[1]}.py") is True:
                rename(f"{plugin_directory}{parameters[1]}.py", f"{plugin_directory}{parameters[1]}.py.disabled")
                await context.edit(f"Plugin {parameters[1]} have been disabled, PagerMaid is restarting.")
                await log(f"Disabled plugin {parameters[1]}.")
                await context.client.disconnect()
            else:
                await context.edit("The plugin specified does not exist.")
        else:
            await context.edit("Invalid arguments.")
    elif parameters[0] == "upload":
        if len(parameters) == 2:
            file_name = f"{parameters[1]}.py"
            reply_id = None
            if reply:
                reply_id = reply.id
            if exists(f"{plugin_directory}{file_name}"):
                copyfile(f"{plugin_directory}{file_name}", file_name)
            elif exists(f"{plugin_directory}{file_name}.disabled"):
                copyfile(f"{plugin_directory}{file_name}.disabled", file_name)
            if exists(file_name):
                await context.edit("Uploading plugin . . .")
                await upload_attachment(file_name,
                                        context.chat_id, reply_id,
                                        caption=f"PagerMaid {parameters[1]} plugin.")
                remove(file_name)
                await context.delete()
            else:
                await context.edit("The plugin specified does not exist.")
        else:
            await context.edit("Invalid arguments.")
    else:
        await context.edit("Invalid arguments.")
