""" The help module. """

from pagermaid import help_messages
from pagermaid.listener import listener


@listener(outgoing=True, command="help",
          description="Shows a list of commands or help string of a single command.",
          parameters="<command>")
async def help(context):
    """ The help command,"""
    if context.arguments:
        if context.arguments in help_messages:
            await context.edit(str(help_messages[context.arguments]))
        else:
            await context.edit("Invalid argument.")
    else:
        result = "**Commands: \n**"
        for command in sorted(help_messages, reverse=False):
            result += "`" + str(command)
            result += "`, "
        await context.edit(result[:-2] + "\n**Issue \"-help <command>\" to view help for a specific command.**")
