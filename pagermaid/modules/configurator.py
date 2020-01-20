""" Pagermaid module to edit the configuration file. """

from pagermaid import config, command_help, log, log_chatid
from pagermaid.listener import listener, diagnostics


@listener(outgoing=True, command="settings")
@diagnostics
async def settings(context):
    return
