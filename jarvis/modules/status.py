""" Module that show system info of the hardware the bot is running on. """

import speedtest
import os

from datetime import datetime
from telethon import functions
from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from platform import python_version, uname
from shutil import which
from telethon import version as telethon_version
from jarvis import command_help, redis_check
from jarvis.events import register
from jarvis.utils import unit_convert

hostname = uname().node
kernel = uname().release


@register(outgoing=True, pattern="^-sysinfo$")
async def sysinfo(context):
    """ Fetches system info using neofetch. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        command = "neofetch --stdout"
        execute = await async_run(
            command,
            stdout=PIPE,
            stderr=PIPE
        )

        stdout, stderr = await execute.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())
        if result == "/bin/sh: neofetch: command not found":
            await context.edit("`Neofetch does not exist on this system.`")
            return
        await context.edit("`" + result + "`")
command_help.update({
    "sysinfo": "Parameter: -sysinfo\
    \nUsage: Retrieve system information via neofetch."
})


@register(outgoing=True, pattern="^-fortune$")
async def fortune(context):
    """ Reads a fortune cookie. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        command = "fortune"
        execute = await async_run(
            command,
            stdout=PIPE,
            stderr=PIPE
        )

        stdout, stderr = await execute.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())
        if result == "/bin/sh: fortune: command not found":
            await context.edit("`No fortune cookies on this system.`")
            return
        await context.edit(result)
command_help.update({
    "fortune": "Parameter: -fortune\
    \nUsage: Reads a fortune cookie message."
})


@register(outgoing=True, pattern="^-tty$")
async def tty(context):
    """ Screenshots a TTY and prints it. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("`Taking screenshot of framebuffer . . .`")
        command = "fbdump | magick - image.png"
        execute = await async_run(
            command,
            stdout=PIPE,
            stderr=PIPE
        )
        message_id_to_reply = context.message.reply_to_msg_id
        if not message_id_to_reply:
            message_id_to_reply = None
        stdout, stderr = await execute.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())
        if result == "/bin/sh: fbdump: command not found":
            await context.edit("`fbdump does not exist on this system.`")
            os.remove("image.png")
            return
        if result == "/bin/sh: convert: command not found":
            await context.edit("`ImageMagick does not exist on this system.`")
            os.remove("image.png")
            return
        if result == "Failed to open /dev/fb0: Permission denied":
            await context.edit("`User not in video group.`")
            os.remove("image.png")
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
        os.remove("image.png")
command_help.update({
    "tty": "Parameter: -tty\
    \nUsage: Takes screenshot of a TTY."
})


@register(outgoing=True, pattern="^-version$")
async def version(context):
    """ Command to query the version of Jarvis. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if which("git") is not None:
            invokever = "git describe --all --long"
            ver = await async_run(
                invokever,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout, stderr = await ver.communicate()
            verout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            invokerev = "git rev-list --all --count"
            rev = await async_run(
                invokerev,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout, stderr = await rev.communicate()
            revout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await context.edit(
                "`Jarvis Version: "
                f"{verout}"
                "` \n"
                "`Git Revision: "
                f"{revout}"
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


@register(outgoing=True, pattern="^-speed$")
async def speed(context):
    """ Tests internet speed using speedtest. """
    result = None
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
command_help.update({
    "speed": "Parameter: -speed\
    \nUsage: Execute the speedtest script and outputs your internet speed."
})


@register(outgoing=True, pattern="^-connection$")
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
