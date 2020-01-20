""" Pagermaid module to edit the configuration file. """

from pagermaid import config, log
from pagermaid.listener import listener


@listener(outgoing=True, command="settings")
async def settings(context):
    return
