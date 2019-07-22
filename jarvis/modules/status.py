""" Module that show system info of the hardware the bot is running on. """

from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from platform import python_version, uname
from shutil import which
# noinspection PyProtectedMember
from telethon import __version__ as telethon_version
from jarvis import command_help, redis_check
from jarvis.events import register

hostname = uname().node
kernel = uname().release


@register(outgoing=True, pattern="^-sysinfo$")
async def sysinfo(context):
    """ Fetches system info using neofetch. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        try:
            command = "neofetch --stdout"
            execute = await async_run(
                command,
                stdout=PIPE,
                stderr=PIPE
            )

            stdout, stderr = await execute.communicate()
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await context.edit("`" + result + "`")
        except FileNotFoundError:
            await context.edit("`Neofetch not found on this system.`")


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
            f"Library version: {telethon_version}"
            "`"
        )


command_help.update({
    "sysinfo": "Parameter: -sysinfo\
    \nUsage: Retrieve system information via neofetch."
})

command_help.update({
    "version": "Parameter: -version\
    \nUsage: Outputs the version and git revision."
})

command_help.update({
    "status": "Parameter: -status\
    \nUsage: Output the status of Jarvis"
})
