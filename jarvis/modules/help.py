""" The help module. """

from jarvis import command_help
from jarvis.events import register

command_help.update({
    "help": "Parameter: -help <command>\
    \nUsage: Shows a list of commands or help string of a single command."
})


@register(outgoing=True, pattern="^-help(?: |$)(.*)")
async def help(context):
    """ The help command,"""
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        args = context.pattern_match.group(1)
        if args:
            if args in command_help:
                await context.edit(str(command_help[args]))
            else:
                await context.edit("`Invalid argument, please check module list.`")
        else:
            result = "**Commands loaded from current modules: \n**"
            for i in command_help:
                result += "`" + str(i)
                result += "`, "
            await context.edit(result[:-2] + "\n**Do \"-help <command>\" to view help for a specific command.**")
