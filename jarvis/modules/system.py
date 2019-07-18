""" System related utilities for Jarvis to integrate into the system. """

import asyncio

from asyncio.subprocess import PIPE
from getpass import getuser
from os import remove
from sys import executable
from jarvis import command_help, log, log_chatid
from jarvis.events import register


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
            await context.edit("`Invalid argument, check module help.`")


command_help.update({
    "pip": "Parameter: -pip <module(s)>\
    \nUsage: Searches pip for the requested modules."
})
