""" Fun related chat utilities. """

from asyncio import sleep
from random import choice
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from cowpy import cow
from pagermaid import bot, path
from pagermaid.listener import listener
from pagermaid.utils import mocker, corrupt, owoifier, execute, random_gen


@listener(outgoing=True, command="animate",
          description="Makes a typing animation via edits to the message.",
          parameters="<message>")
async def animate(context):
    """ Animate a message. """
    text = await context.get_reply_message()
    message = context.pattern_match.group(1)
    if message:
        pass
    elif text:
        message = text.text
    else:
        await context.edit("Invalid argument.")
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


@listener(outgoing=True, command="mock",
          description="Mock people by weirdly capitalizing their messages.",
          parameters="<message>")
async def mock(context):
    """ Mock people with weird capitalization. """
    reply = await context.get_reply_message()
    message = context.pattern_match.group(1)
    if message:
        pass
    elif reply:
        message = reply.text
    else:
        await context.edit("Invalid arguments.")
        return

    reply_text = mocker(message)
    if reply:
        if reply.sender.is_self:
            try:
                await reply.edit(reply_text)
            except MessageNotModifiedError:
                await context.edit("This message is already mocked in the same way.")
                return
            await context.delete()
    else:
        await context.edit(reply_text)


@listener(outgoing=True, command="widen",
          description="Widens every character in a string.",
          parameters="<string>")
async def widen(context):
    """ Widens every character in a string. """
    reply = await context.get_reply_message()
    message = context.pattern_match.group(1)
    if message:
        pass
    elif reply:
        message = reply.text
    else:
        await context.edit("Invalid argument.")
        return
    wide_map = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
    wide_map[0x20] = 0x3000
    reply_text = str(message).translate(wide_map)
    if reply:
        if reply.sender.is_self:
            try:
                await reply.edit(reply_text)
            except MessageNotModifiedError:
                await context.edit("This message is already widened.")
                return
            await context.delete()
    else:
        await context.edit(reply_text)


@listener(outgoing=True, command="fox",
          description="Makes a fox scratch your message.",
          parameters="<message>")
async def fox(context):
    """ Makes a fox scratch your message. """
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


@listener(outgoing=True, command="owo",
          description="Converts normal messages to OwO.",
          parameters="<message>")
async def owo(context):
    """ Makes messages become OwO. """
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


@listener(outgoing=True, command="ship",
          description="Generates random couple, supports specifying the target as well.",
          parameters="<username> <username>")
async def ship(context):
    """ Ship randomly generated members. """
    await context.edit("Generating couple . . .")
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


@listener(outgoing=True, command="aaa",
          description="Saves a few presses of the A and shift key.",
          parameters="<integer>")
async def aaa(context):
    """ Saves a few presses of the A and shift key. """
    await random_gen(context, "Aa")


@listener(outgoing=True, command="asciiart",
          description="Generates ASCII art for specified string.",
          parameters="<string>")
async def asciiart(context):
    """ Generates ASCII art for specified string. """
    if not context.pattern_match.group(1):
        await context.edit("`Invalid arguments.`")
        return
    output = await execute(f"figlet -f {path}/assets/graffiti.flf '{context.pattern_match.group(1)}'")
    await context.edit(f"`{output}`")


@listener(outgoing=True, command="tuxsay",
          description="Generates ASCII art of Tux saying a specific message.",
          parameters="<message>")
async def tuxsay(context):
    """ Generates ASCII art of Tux saying stuff for specified string. """
    if not context.pattern_match.group(1):
        await context.edit("`Invalid arguments.`")
        return
    await context.edit(f"```{cow.Tux().milk(context.pattern_match.group(1))} \n ```")


@listener(outgoing=True, command="coin",
          description="Throws a coin.")
async def coin(context):
    await context.edit("Throwing coin . . .")
    await sleep(.5)
    outcomes = ['A'] * 5 + ['B'] * 5 + ['C'] * 1
    result = choice(outcomes)
    count = 0
    while count <= 3:
        await context.edit("`.` . .")
        await sleep(.3)
        await context.edit(". `.` .")
        await sleep(.3)
        await context.edit(". . `.`")
        await sleep(.3)
        count += 1
    if result == "C":
        await context.edit("WAAAHHH I LOST THE COIN")
    elif result == "B":
        await context.edit("Tails!")
    elif result == "A":
        await context.edit("Heads!")


@listener(outgoing=True, pattern="^OwO$")
async def wink(context):
    """ OwO """
    await context.edit("OwU")
    await sleep(.3)
    await context.edit("OwO")
