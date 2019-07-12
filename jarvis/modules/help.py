""" The help module. """

from jarvis import command_help
from jarvis.events import register


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
            await context.edit("`Invalid argument, please specify target module.`")
            string = ""
            for i in command_help:
                string += "`" + str(i)
                string += "`\n"
            await context.reply(string)
