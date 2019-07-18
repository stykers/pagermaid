""" System related utilities for Jarvis to integrate into the system. """

import asyncio
import platform

from asyncio.subprocess import PIPE
from getpass import getuser
from os import remove
from os import geteuid
from sys import executable
from jarvis import command_help, log, log_chatid
from jarvis.events import register


@register(outgoing=True, pattern="^-sh(?: |$)(.*)")
async def sh(context):
    """ For calling a binary from the shell. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        user = getuser()
        command = context.pattern_match.group(1)
        uid = geteuid()
        hostname = platform.node()
        if context.is_channel and not context.is_group:
            await context.edit("`Current configuration disables shell execution in channel.`")
            return

        if not command:
            await context.edit("`Invalid argument.`")
            return

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=PIPE,
            stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if len(result) > 4096:
            output = open("output.txt", "w+")
            output.write(result)
            output.close()
            await context.client.send_file(
                context.chat_id,
                "output.log",
                reply_to=context.id,
                caption="`Output exceeded limit, attaching file.`",
            )
            remove("output.txt")
            return

        if uid is 0:
            await context.edit(
                f"`{user}`@{hostname} ~"
                f"\n> `#` {command}"
                f"\n`{result}`"
            )
        else:
            await context.edit(
                f"`{user}`@{hostname} ~"
                f"\n> `$` {command}"
                f"\n`{result}`"
            )

        if log:
            await context.client.send_message(
                log_chatid,
                "Command `" + command + "` executed.",
            )


@register(outgoing=True, pattern="^-pip(?: |$)(.*)")
async def pip(context):
    """ Search pip for module. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        pipmodule = context.pattern_match.group(1)
        if pipmodule:
            await context.edit("`Searching pip for module . . .`")
            command = f"pip search {pipmodule}"
            execute = await asyncio.create_subprocess_shell(
                command,
                stdout=PIPE,
                stderr=PIPE,
            )

            stdout, stderr = await execute.communicate()
            pipout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            if pipout:
                if len(pipout) > 4096:
                    await context.edit("`Output exceeded limit, attaching file.`")
                    file = open("output.log", "w+")
                    file.write(pipout)
                    file.close()
                    await context.client.send_file(
                        context.chat_id,
                        "output.log",
                        reply_to=context.id,
                    )
                    remove("output.log")
                    return
                await context.edit(
                    "**Command: **\n`"
                    f"{command}"
                    "`\n**Output: **\n`"
                    f"{pipout}"
                    "`"
                )
            else:
                await context.edit(
                    "**Command: **\n`"
                    f"{command}"
                    "`\n**Output: **\n`No output.`"
                )
        else:
            await context.edit("`Invalid argument.`")


command_help.update({
    "pip": "Parameter: -pip <module(s)>\
    \nUsage: Searches pip for the requested modules."
})
