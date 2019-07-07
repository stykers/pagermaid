""" The help module. """

from jarvis import command_help
from jarvis.events import register


@register(outgoing=True, pattern="^s!help(?: |$)(.*)")
async def help(event):
    """ The help command. """
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        args = event.pattern_match.group(1)
        if args:
            if args in command_help:
                await event.edit(str(command_help[args]))
            else:
                await event.edit("Invalid argument, please check module list.")
        else:
            await event.edit("Invalid argument, please specify target module.")
            result = ""
            for i in command_help:
                result += '`' + str(i)
                result += "`\n"
            await event.reply(result)
