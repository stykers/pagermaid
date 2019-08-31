""" Module that show system info of the hardware the bot is running on. """

from os import remove
from datetime import datetime
from speedtest import Speedtest
from telethon import functions
from platform import python_version, uname
from shutil import which
from telethon import version as telethon_version
from jarvis import command_help, redis_check
from jarvis.events import register, diagnostics
from jarvis.utils import unit_convert, execute


hostname = uname().node
kernel = uname().release


@register(outgoing=True, pattern="^-sysinfo$")
@diagnostics
async def sysinfo(context):
    """ Fetches system info using neofetch. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        result = await execute("neofetch --stdout")
        if result == "/bin/sh: neofetch: command not found":
            await context.edit("`Neofetch does not exist on this system.`")
            return
        await context.edit("`" + result + "`")
command_help.update({
    "sysinfo": "Parameter: -sysinfo\
    \nUsage: Retrieve system information via neofetch."
})


@register(outgoing=True, pattern="^-fortune$")
@diagnostics
async def fortune(context):
    """ Reads a fortune cookie. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        result = await execute("fortune")
        if result == "/bin/sh: fortune: command not found":
            await context.edit("`No fortune cookies on this system.`")
            return
        await context.edit(result)
command_help.update({
    "fortune": "Parameter: -fortune\
    \nUsage: Reads a fortune cookie message."
})


@register(outgoing=True, pattern="^-tty$")
@diagnostics
async def tty(context):
    """ Screenshots a TTY and prints it. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
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


@register(outgoing=True, pattern="^-version$")
@diagnostics
async def version(context):
    """ Command to query the version of Jarvis. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if which("git") is not None:
            version_result = await execute("git describe --all --long")
            revision_result = await execute("git rev-list --all --count")

            await context.edit(
                "`Jarvis Version: "
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


@register(outgoing=True, pattern="^-status$")
@diagnostics
async def status(context):
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if not redis_check():
            db = "Redis is malfunctioning."
        else:
            db = "Connected to Redis."
        await context.edit(
            "`"
            "Jarvis is online. \n\n"
            f"Hostname: {hostname} \n"
            f"Database Status: {db} \n"
            f"Kernel Version: {kernel} \n"
            f"Python Version: {python_version()} \n"
            f"Library version: {telethon_version.__version__}"
            "`"
        )
command_help.update({
    "status": "Parameter: -status\
    \nUsage: Output the status of Jarvis"
})


@register(outgoing=True, pattern="^-speedtest$")
@diagnostics
async def speedtest(context):
    """ Tests internet speed using speedtest. """
    result = None
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
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
    "speed": "Parameter: -speed\
    \nUsage: Execute the speedtest script and outputs your internet speed."
})


@register(outgoing=True, pattern="^-connection$")
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


@register(outgoing=True, pattern="^-ping$")
@diagnostics
async def ping(context):
    """ Calculates the latency of the bot host. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        start = datetime.now()
        await context.edit("`Pong!`")
        end = datetime.now()
        duration = (end - start).microseconds / 1000
        await context.edit("`Pong!|%sms`" % duration)
command_help.update({
    "ping": "Parameter: -ping\
    \nUsage: Outputs your latency to telegram."
})
