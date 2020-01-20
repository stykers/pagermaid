""" The help module. """

from pagermaid import help_messages
from pagermaid.listener import listener


@listener(outgoing=True, command="help",
          description="Shows a list of commands or help string of a single command.",
          parameters="<command>")
async def help(context):
    """ The help command,"""
    args = context.pattern_match.group(1)
    if args:
        if args in help_messages:
            await context.edit(str(help_messages[args]))
        else:
            await context.edit("Invalid argument.")
    else:
        result = "**Commands loaded from current modules: \n**"
        for i in sorted(help_messages, reverse=False):
            result += "`" + str(i)
            result += "`, "
        await context.edit(result[:-2] + "\n**Do \"-help <command>\" to view help for a specific command.**")
