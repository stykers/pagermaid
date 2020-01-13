""" The help module. """

from pagermaid import command_help
from pagermaid.listener import listener, diagnostics


@listener(outgoing=True, command="help")
@diagnostics
async def help(context):
    """ The help command,"""
    args = context.pattern_match.group(1)
    if args:
        if args in command_help:
            await context.edit(str(command_help[args]))
        else:
            await context.edit("`Invalid argument, please check module list.`")
    else:
        result = "**Commands loaded from current modules: \n**"
        for i in sorted(command_help, reverse=False):
            result += "`" + str(i)
            result += "`, "
        await context.edit(result[:-2] + "\n**Do \"-help <command>\" to view help for a specific command.**")


command_help.update({
    "help": "Parameter: -help <command>\
    \nUsage: Shows a list of commands or help string of a single command."
})
