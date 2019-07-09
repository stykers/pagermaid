""" Module that show system info of the hardware the bot is running on. """

from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from platform import python_version, uname
from shutil import which
from os import remove
from telethon import version
from jarvis import command_help, redis, redis_check
from jarvis.events import register


hostname = uname().node
kernel = uname().release


@register(outgoing=True, pattern="^-sysinfo$")
async def sysinfo(sys):
    """ Fetches system info using neofetch. """
    if not sys.text[0].isalpha() and sys.text[0] not in ("/", "#", "@", "!"):
        try :
            command = "neofetch --stdout"
            execute = await async_run(
                command,
                stdout=PIPE,
                stderr=PIPE
            )

            stdout, stderr = await execute.communicate()
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await sys.edit("`" + result + "`")
        except FileNotFoundError:
            await sys.edit("`Neofetch not found on this system.`")


@register(outgoing=True, pattern="^-version$")
async def bot_ver(event):
    """ Command to query the version of the bot. """
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
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

            await event.edit(
                "`Jarvis Version: "
                f"{verout}"
                "` \n"
                "`Git Revision: "
                f"{revout}"
                "`"
            )
        else:
            await event.edit(
                "Git is malfunctioning."
            )


@register(outgoing=True, pattern="^-status$")
async def status(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        if not redis_check():
            db = "Redis is malfunctioning."
        else:
            db = "Connected to Redis."
        await e.edit(
            "`"
            "Jarvis is online. \n\n"
            f"Hostname: {hostname} \n"
            f"Database Status: {db} \n"
            f"Kernel Version: {kernel} \n"
            f"Python Version: {python_version()} \n"
            f"Library version: {version.__version__}"
            "`"
            )


@register(outgoing=True, pattern="^-pip(?: |$)(.*)")
async def pip(module):
    """ Search pip for module. """
    if not module.text[0].isalpha() and module.text[0] not in ("/", "#", "@", "!"):
        pipmodule = module.pattern_match.group(1)
        if pipmodule:
            await module.edit("`Searching pip for module . . .`")
            command = f"pip search {pipmodule}"
            execute = await async_run(
                command,
                stdout=PIPE,
                stderr=PIPE,
            )

            stdout, stderr = await execute.communicate()
            pipout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            if pipout:
                if len(pipout) > 4096:
                    await module.edit("`Output too large, sending as file`")
                    file = open("output.txt", "w+")
                    file.write(pipout)
                    file.close()
                    await module.client.send_file(
                        module.chat_id,
                        "output.txt",
                        reply_to=module.id,
                    )
                    remove("output.txt")
                    return
                await module.edit(
                    "**Command: **\n`"
                    f"{command}"
                    "`\n**Output: **\n`"
                    f"{pipout}"
                    "`"
                )
            else:
                await module.edit(
                    "**Command: **\n`"
                    f"{command}"
                    "`\n**Output: **\n`No output.`"
                )
        else:
            await module.edit("`Invalid argument, check module help.`")
