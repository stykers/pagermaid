""" Fun related chat utilities. """

from asyncio import sleep
from random import choice
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from cowpy import cow
from pagermaid import command_help, bot
from pagermaid.listener import listener, diagnostics
from pagermaid.utils import mocker, corrupt, owoifier, execute, random_gen


@listener(command="animate")
@diagnostics
async def animate(context):
    """ Command for animated texts. """
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


@listener(outgoing=True, command="mock")
@diagnostics
async def mock(context):
    """ Mock people with weird caps. """
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


@listener(outgoing=True, command="widen")
@diagnostics
async def widen(context):
    """ Make texts weirdly wide. """
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


@listener(outgoing=True, command="fox")
@diagnostics
async def fox(context):
    """ Make a fox scratch your message. """
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


@listener(outgoing=True, command="owo")
@diagnostics
async def owo(context):
    """ Makes messages become owo. """
    if context.pattern_match.group(1):
        text = context.pattern_match.group(1)
        await context.edit(owoifier(text))
        return
    elif context.reply_to_msg_id:
        reply_msg = await context.get_reply_message()
        if reply_msg.sender.is_self:
            try:
                result = owoifier(reply_msg.text)
            except BaseException:
                await context.delete()
                return
            await reply_msg.edit(result)
            await context.delete()
        else:
            try:
                result = owoifier(reply_msg.text)
            except BaseException:
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


@listener(outgoing=True, command="ship")
@diagnostics
async def ship(context):
    """ Ship randomly generated members. """
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
    if len(users) == 1:
        target_1 = users[0]
        target_2 = await bot.get_me()
    await context.edit("**Generated couple**\n"
                       + f"[{target_1.first_name}](tg://user?id={target_1.id})" + " + "
                       + f"[{target_2.first_name}](tg://user?id={target_2.id})" + " = " + "❤️")


command_help.update({
    "ship": "Parameter: -ship <user> <user>\
    \nUsage: Ships random person, supports defining person to ship."
})


@listener(outgoing=True, command="aaa")
@diagnostics
async def aaa(context):
    """ Generates screams. """
    await random_gen(context, "Aa")


command_help.update({
    "aaa": "Parameter: -aaa <integer>\
    \nUsage: Generates screams."
})


@listener(outgoing=True, command="asciiart")
@diagnostics
async def asciiart(context):
    """ Generates ASCII art for provided strings. """
    if not context.pattern_match.group(1):
        await context.edit("`Invalid arguments.`")
        return
    output = await execute(f"figlet -f ./utils/graffiti.flf '{context.pattern_match.group(1)}'")
    await context.edit(f"`{output}`")


command_help.update({
    "asciiart": "Parameter: -asciiart <text>\
     \nUsage: Generates ASCII art for target text."
})


@listener(outgoing=True, command="tuxsay")
@diagnostics
async def tuxsay(context):
    """ Generates ASCII art for Tux saying stuff. """
    if not context.pattern_match.group(1):
        await context.edit("`Invalid arguments.`")
        return
    await context.edit(f"```{cow.Tux().milk(context.pattern_match.group(1))} \n ```")


command_help.update({
    "asciiart": "Parameter: -asciiart <text>\
     \nUsage: Generates ASCII art for target text."
})


@listener(outgoing=True, pattern="^OwO$")
async def wink(context):
    """ OwO """
    await context.edit("OwU")
    await sleep(.3)
    await context.edit("OwO")
