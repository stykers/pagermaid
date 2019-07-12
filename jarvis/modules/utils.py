""" Useful utilities for Jarvis. """
import speedtest

from datetime import datetime
from telethon import functions
from jarvis import command_help, bot, log, log_chatid
from jarvis.events import register


@register(outgoing=True, pattern="^-userid$")
async def userid(context):
    """ Queries the userid of a user. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        message = await context.get_reply_message()
        if message:
            if not message.forward:
                user_id = message.sender.id
                if message.sender.username:
                    name = "@" + message.sender.username
                else:
                    name = "**" + message.sender.first_name + "**"

            else:
                user_id = message.forward.sender.id
                if message.forward.sender.username:
                    name = "@" + message.forward.sender.username
                else:
                    name = "*" + message.forward.sender.first_name + "*"
            await context.edit(
                "**Username:** {} \n**UserID:** `{}`"
                .format(name, user_id)
            )


@register(outgoing=True, pattern="^-chatid$")
async def chatid(context):
    """ Queries the chatid of the chat you are in. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("ChatID: `" + str(context.chat_id) + "`")


@register(outgoing=True, pattern=r"^-log(?: |$)([\s\S]*)")
async def log(context):
    """ Forwards a message into log group """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if log:
            if context.reply_to_msg_id:
                reply_msg = await context.get_reply_message()
                await reply_msg.forward_to(log_chatid)
            elif context.pattern_match.group(1):
                user = f"#LOG / Chat ID: {context.chat_id}\n\n"
                text = user + context.pattern_match.group(1)
                await bot.send_message(log_chatid, text)
            else:
                await context.edit("`Specify target message.`")
                return
            await context.edit("Noted.")
        else:
            await context.edit("`Logging is disabled.`")


@register(outgoing=True, pattern="^-leave$")
async def leave(context):
    """ It leaves you from the group. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Goodbye.")
        try:
            await bot(functions.channels.LeaveChannelRequest(leave.chat_id))
        except AttributeError:
            await context.edit("You are not in a group.")


@register(outgoing=True, pattern="^-shutdown$")
async def shutdown(context):
    """ To shutdown Jarvis. """
    if not context.text[0].isalpha():
        await context.edit("`Jarvis is powering off.`")
        if log:
            await context.client.send_message(
                log_chatid,
                "Jarvis power off."
            )
        await context.client.disconnect()


@register(outgoing=True, pattern="^-channel$")
async def channel(context):
    """ Returns the author's channel. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Author Channel: @SparkzStuff")


@register(outgoing=True, pattern="^-source$")
async def source(context):
    """ Prints the git repository URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://git.stykers.moe/scm/~stykers/jarvis.git")


@register(outgoing=True, pattern="^-speed$")
async def speed(context):
    """ Tests internet speed using speedtest. """
    global result
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("`Executing test scripts . . .`")
        test = speedtest.Speedtest()

        test.get_best_server()
        test.download()
        test.upload()
        test.results.share()
        result = test.results.dict()

    await context.edit("Timestamp "
                       f"`{result['timestamp']}` \n\n"
                       "Upload "
                       f"`{unit_convert(result['upload'])}` \n"
                       "Download "
                       f"`{unit_convert(result['download'])}` \n"
                       "Latency "
                       f"`{result['ping']}` \n"
                       "ISP "
                       f"`{result['client']['isp']}`")


@register(outgoing=True, pattern="^-connection$")
async def connection(context):
    """ Shows connection info. """
    datacenter = await context.client(functions.help.GetNearestDcRequest())
    await context.edit(
        f"Region `{datacenter.country}` \n"
        f"Connected Datacenter `{datacenter.this_dc}` \n"
        f"Nearest Datacenter `{datacenter.nearest_dc}`"
    )


@register(outgoing=True, pattern="^-ping$")
async def ping(context):
    """ Calculates the latency of the bot host. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        start = datetime.now()
        await context.edit("`Pong!`")
        end = datetime.now()
        duration = (end - start).microseconds / 1000
        await context.edit("`Pong!|%sms`" % duration)


def unit_convert(byte):
    """ Converts byte into readable formats. """
    power = 2 ** 10
    zero = 0
    units = {
        0: '',
        1: 'Kb/s',
        2: 'Mb/s',
        3: 'Gb/s',
        4: 'Tb/s'}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"


command_help.update({
    "chatid": "Parameter: -chatid\
    \nUsage: Query the chatid of the chat you are in"
})
command_help.update({
    "userid": "Parameter: -userid\
    \nUsage: Query the userid of the sender of the message you replied to."
})
command_help.update({
    "log": "Parameter: -log\
    \nUsage: Forwards message to logging group."
})
command_help.update({
    "leave": "Parameter: -leave\
    \nUsage: Say goodbye and leave."
})
command_help.update({
    "shutdown": "Parameter: -shutdown\
    \nUsage: Shuts down Jarvis."
})
command_help.update({
    "channel": "Parameter: -channel\
    \nUsage: Shows the development channel."
})
command_help.update({
    "source": "Parameter: -source\
    \nUsage: Prints the git repository URL."
})

command_help.update({
    "speed": "Parameter: -speed\
    \nUsage: Execute the speedtest script and outputs your internet speed."
})

command_help.update({
    "connection": "Parameter: -connection\
    \nUsage: Shows your connection info."
})

command_help.update({
    "ping": "Parameter: -ping\
    \nUsage: Outputs your latency to telegram."
})
