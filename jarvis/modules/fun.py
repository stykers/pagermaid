""" Fun related chat utilities. """

from asyncio import sleep
from random import choice
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from jarvis import command_help, bot
from jarvis.events import register
from jarvis.utils import mocker, corrupt, owoifier


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
        latency = 0.03
        cursor = "█"
        old_text = ''
        await context.edit(cursor)
        await sleep(latency)
        for character in message:
            old_text = old_text + "" + character
            typing_text = old_text + "" + cursor
            await context.edit(typing_text)
            await sleep(latency)
            await context.edit(old_text)
            await sleep(latency)
command_help.update({
    "animate": "Parameter: -animate <text>\
    \nUsage: Animated text via edit."
})


@register(outgoing=True, pattern="^-mock(?: |$)(.*)")
async def mock(context):
    """ Mock people with weird caps. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        reply = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif reply:
            message = reply.text
        else:
            await context.edit("`Invalid arguments.`")
            return

        reply_text = mocker(message)
        if reply:
            if reply.sender.is_self:
                try:
                    await reply.edit(reply_text)
                except MessageNotModifiedError:
                    await context.edit("`This message is already mocked in the same way.`")
                    return
                await context.delete()
        else:
            await context.edit(reply_text)
command_help.update({
    "mock": "Parameter: -mock <text>\
    \nUsage: Mock a string via weird caps."
})


@register(outgoing=True, pattern="^-widen(?: |$)(.*)")
async def widen(context):
    """ Make texts weirdly wide. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        reply = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif reply:
            message = reply.text
        else:
            await context.edit("`Invalid argument.`")
            return

        reply_text = str(message).translate(dict((i, i + 0xFEE0) for i in range(0x21, 0x7F)))
        if reply:
            if reply.sender.is_self:
                try:
                    await reply.edit(reply_text)
                except MessageNotModifiedError:
                    await context.edit("`This message is already widened.`")
                    return
                await context.delete()
        else:
            await context.edit(reply_text)
command_help.update({
    "widen": "Parameter: -widen <text>\
    \nUsage: Widen every char in a string in a weird way."
})


@register(outgoing=True, pattern="^-fox(?: |$)(.*)")
async def fox(context):
    """ Make a fox scratch your message. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        reply = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif reply:
            message = reply.text
        else:
            await context.edit(
                "`Invalid arguments.`"
            )
            return

        input_text = " ".join(message).lower()
        reply_text = corrupt(input_text)
        if reply:
            if reply.sender.is_self:
                try:
                    await reply.edit(reply_text)
                except MessageNotModifiedError:
                    await context.edit("`Message have already been scratched.`")
                await context.delete()
            else:
                await context.edit(reply_text)
command_help.update({
    "fox": "Parameter: -fox <text>\
    \nUsage: Make a fox corrupt your text."
})


@register(outgoing=True, pattern=r"^-owo(?: |$)([\s\S]*)")
async def owo(context):
    """ Makes messages become owo. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.pattern_match.group(1):
            text = context.pattern_match.group(1)
            await context.edit(owoifier(text))
            return
        elif context.reply_to_msg_id:
            reply_msg = await context.get_reply_message()
            if reply_msg.sender.is_self:
                try:
                    result = owoifier(reply_msg.text)
                except:
                    await context.delete()
                    return
                await reply_msg.edit(result)
                await context.delete()
            else:
                try:
                    result = owoifier(reply_msg.text)
                except:
                    await context.delete()
                    return
                await context.edit(result)
            return
        else:
            await context.edit("`Unable to get the target message.`")
            return
command_help.update({
    "owo": "Parameter: -owo <text>\
    \nUsage: Converts messages to OwO."
})


@register(outgoing=True, pattern="^-ship(?: |$)(.*)")
async def ship(context):
    """ Ship randomly generated members. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("`Generating couple . . .`")
        users = []
        async for user in context.client.iter_participants(context.chat_id):
            users.append(user)
        target_1 = choice(users)
        target_2 = choice(users)
        if context.pattern_match.group(1):
            if ' ' in context.pattern_match.group(1):
                string_1, string_2 = context.pattern_match.group(1).split(' ', 1)
                user = string_1
                if user.isnumeric():
                    user = int(user)
                try:
                    target_1 = await context.client.get_entity(user)
                except (TypeError, ValueError) as err:
                    await context.edit(str(err))
                    return None
                user = string_2
                if user.isnumeric():
                    user = int(user)
                try:
                    target_2 = await context.client.get_entity(user)
                except (TypeError, ValueError) as err:
                    await context.edit(str(err))
                    return None
            else:
                string_1 = context.pattern_match.group(1)
                user = string_1
                if user.isnumeric():
                    user = int(user)
                try:
                    target_1 = await context.client.get_entity(user)
                except (TypeError, ValueError) as err:
                    await context.edit(str(err))
                    return None
        if len(users) is 1:
            target_1 = users[0]
            target_2 = await bot.get_me()
        if not context.message.sender.is_self:
            await context.client.send_message(context.chat_id, "**Generated couple**\n"
                                              + f"[{target_1.first_name}](tg://user?id={target_1.id})" + " + "
                                              + f"[{target_2.first_name}](tg://user?id={target_2.id})" + " = " + "❤️")
        else:
            await context.edit("**Generated couple**\n"
                               + f"[{target_1.first_name}](tg://user?id={target_1.id})" + " + "
                               + f"[{target_2.first_name}](tg://user?id={target_2.id})" + " = " + "❤️")


command_help.update({
    "ship": "Parameter: -ship <user> <user>\
    \nUsage: Ships random person, supports defining person to ship."
})
