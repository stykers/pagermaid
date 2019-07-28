""" Fun related chat utilities. """

import asyncio

from zalgo_text import zalgo
from spongemock import spongemock
from jarvis import command_help
from jarvis.events import register


@register(pattern='-animate(?: |$)(.*)')
async def animate(context):
    """ Command for animated texts. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid argument.`")
            return
        sleep_time = 0.03
        typing_symbol = "█"
        old_text = ''
        await context.edit(typing_symbol)
        await asyncio.sleep(sleep_time)
        for character in message:
            old_text = old_text + "" + character
            typing_text = old_text + "" + typing_symbol
            await context.edit(typing_text)
            await asyncio.sleep(sleep_time)
            await context.edit(old_text)
            await asyncio.sleep(sleep_time)


@register(outgoing=True, pattern="^-mock(?: |$)(.*)")
async def mock(context):
    """ Mock people with weird caps. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid arguments.`")
            return

        result = spongemock.mock(message)
        await context.edit(result)


@register(outgoing=True, pattern="^-widen(?: |$)(.*)")
async def widen(context):
    """ Make texts weirdly wide. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid argument.`")
            return

        reply_text = str(message).translate(dict((i, i + 0xFEE0) for i in range(0x21, 0x7F)))
        await context.edit(reply_text)


@register(outgoing=True, pattern="^-fox(?: |$)(.*)")
async def fox(context):
    """ Make a fox scratch your message. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit(
                "`Invalid arguments.`"
            )
            return

        input_text = " ".join(message).lower()
        corrupted_text = zalgo.zalgo().zalgofy(input_text)
        await context.edit(corrupted_text)


command_help.update({
    "animate": "Parameter: -animate <text>\
    \nUsage: Animated text."
})

command_help.update({
    "mock": "Parameter: -mock <text>\
    \nUsage: Mock a string via weird caps."
})

command_help.update({
    "widen": "Parameter: -widen <text>\
    \nUsage: Widen every char in a string in a weird way."
})

command_help.update({
    "fox": "Parameter: -fox <text>\
    \nUsage: Make a fox corrupt your text."
})
