""" Module that show system info of the hardware the bot is running on. """

from os import remove
from datetime import datetime
from speedtest import Speedtest
from telethon import functions
from platform import python_version, uname
from shutil import which
from telethon import version as telethon_version
from sys import platform
from pagermaid import command_help, redis_check
from pagermaid.listener import listener, diagnostics
from pagermaid.utils import unit_convert, execute, make_top_cloud

hostname = uname().node
kernel = uname().release


@listener(outgoing=True, command="sysinfo")
@diagnostics
async def sysinfo(context):
    """ Fetches system info using neofetch. """
    result = await execute("neofetch --config none --stdout")
    await context.edit("`" + result + "`")


command_help.update({
    "sysinfo": "Parameter: -sysinfo\
    \nUsage: Retrieve system information via neofetch."
})


@listener(outgoing=True, command="fortune")
@diagnostics
async def fortune(context):
    """ Reads a fortune cookie. """
    result = await execute("fortune")
    if result == "/bin/sh: fortune: command not found":
        await context.edit("`No fortune cookies on this system.`")
        return
    await context.edit(result)


command_help.update({
    "fortune": "Parameter: -fortune\
    \nUsage: Reads a fortune cookie message."
})


@listener(outgoing=True, command="tty")
@diagnostics
async def tty(context):
    """ Screenshots a TTY and prints it. """
    await context.edit("`Taking screenshot of framebuffer . . .`")
    message_id_to_reply = context.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    result = await execute("fbdump | magick - image.png")
    if result == "/bin/sh: fbdump: command not found":
        await context.edit("`fbdump does not exist on this system.`")
        remove("image.png")
        return
    if result == "/bin/sh: convert: command not found":
        await context.edit("`ImageMagick does not exist on this system.`")
        remove("image.png")
        return
    if result == "Failed to open /dev/fb0: Permission denied":
        await context.edit("`User not in video group.`")
        remove("image.png")
        return
    try:
        await context.client.send_file(
            context.chat_id,
            "image.png",
            caption="Screenshot of currently attached tty.",
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply
        )
    except ValueError:
        await context.edit("`File is not generated due to unexpected error.`")
        return
    await context.delete()
    remove("image.png")


command_help.update({
    "tty": "Parameter: -tty\
    \nUsage: Takes screenshot of a TTY."
})


@listener(outgoing=True, command="version")
@diagnostics
async def version(context):
    """ Command to query the version of PagerMaid. """
    if which("git") is not None:
        version_result = await execute("git describe --all --long")
        revision_result = await execute("git rev-list --all --count")

        await context.edit(
            "`PagerMaid Version: "
            f"{version_result}"
            "` \n"
            "`Git Revision: "
            f"{revision_result}"
            "`"
        )
    else:
        await context.edit(
            "Git is malfunctioning."
        )


command_help.update({
    "version": "Parameter: -version\
    \nUsage: Outputs the version and git revision."
})


@listener(outgoing=True, command="status")
@diagnostics
async def status(context):
    if not redis_check():
        db = "Redis is malfunctioning."
    else:
        db = "Connected to Redis."
    await context.edit(
        "`"
        "PagerMaid is online. \n\n"
        f"Hostname: {hostname} \n"
        f"Database Status: {db} \n"
        f"Host Platform: {platform} \n"
        f"Kernel Version: {kernel} \n"
        f"Python Version: {python_version()} \n"
        f"Library version: {telethon_version.__version__}"
        "`"
    )


command_help.update({
    "status": "Parameter: -status\
    \nUsage: Output the status of PagerMaid"
})


@listener(outgoing=True, command="speedtest")
@diagnostics
async def speedtest(context):
    """ Tests internet speed using speedtest. """
    result = None
    await context.edit("`Executing test scripts . . .`")
    test = Speedtest()

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


command_help.update({
    "speedtest": "Parameter: -speedtest\
    \nUsage: Execute the speedtest script and outputs your internet speed."
})


@listener(outgoing=True, command="connection")
@diagnostics
async def connection(context):
    """ Shows connection info. """
    datacenter = await context.client(functions.help.GetNearestDcRequest())
    await context.edit(
        f"Region `{datacenter.country}` \n"
        f"Connected Datacenter `{datacenter.this_dc}` \n"
        f"Nearest Datacenter `{datacenter.nearest_dc}`"
    )


command_help.update({
    "connection": "Parameter: -connection\
    \nUsage: Shows your connection info."
})


@listener(outgoing=True, command="ping")
@diagnostics
async def ping(context):
    """ Calculates the latency of the bot host. """
    start = datetime.now()
    await context.edit("`Pong!`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await context.edit("`Pong!|%sms`" % duration)


command_help.update({
    "ping": "Parameter: -ping\
    \nUsage: Outputs your latency to telegram."
})


@listener(outgoing=True, command="topcloud")
@diagnostics
async def topcloud(context):
    """ Generates a word cloud of resource-hungry processes. """
    if context.fwd_from:
        return
    await make_top_cloud(context)
    await context.edit("Uploading image . . .")
    await context.client.send_file(
        context.chat_id,
        "cloud.png",
        reply_to=None,
        caption="Cloud of running processes."
    )
    remove("cloud.png")
    await context.delete()


command_help.update({
    "topcloud": "Parameter: -topcloud <image>\
    \nUsage: Generates a word cloud of resource-hungry processes."
})
