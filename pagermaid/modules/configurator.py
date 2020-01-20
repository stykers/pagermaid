""" Pagermaid module to edit the configuration file. """

from pagermaid import config, command_help, log, log_chatid
from pagermaid.listener import listener


@listener(outgoing=True, command="settings")
async def settings(context):
    return
