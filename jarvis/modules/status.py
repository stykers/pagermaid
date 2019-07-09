""" Module that show system info of the hardware the bot is running on. """

from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from platform import python_version, uname
from shutil import which
from os import remove
from telethon import version
from jarvis import command_help, redis, redis_check
from jarvis.events import register


default_user = uname().node


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
