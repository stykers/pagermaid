""" The help module. """

from jarvis import command_help
from jarvis.events import register


@register(outgoing=True, pattern="^-help(?: |$)(.*)")
async def help(event):
    """ The help command,"""
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        args = event.pattern_match.group(1)
        if args:
            if args in command_help:
                await event.edit(str(command_help[args]))
            else:
                await event.edit("`Invalid argument, please check module list.`")
        else:
            await event.edit("`Invalid argument, please specify target module.`")
            string = ""
            for i in command_help:
                string += "`" + str(i)
                string += "`\n"
            await event.reply(string)
