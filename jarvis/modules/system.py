""" System related utilities for Jarvis to integrate into the system. """

import asyncio
import platform
from asyncio.subprocess import PIPE
from getpass import getuser
from os import remove
from os import geteuid
from jarvis import command_help, log, log_chatid
from jarvis.events import register


@register(outgoing=True, pattern="^-evaluate(?: |$)(.*)")
async def evaluate(context):
    """ Evaluate a python expression. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.is_channel and not context.is_group:
            await context.edit("`Evaluation is disabled in channels.`")
            return

        if context.pattern_match.group(1):
            expression = context.pattern_match.group(1)
        else:
            await context.edit("`Invalid parameter.`")
            return

        try:
            evaluation = str(eval(expression))
            if evaluation:
                if isinstance(evaluation, str):
                    if len(evaluation) >= 4096:
                        file = open("output.log", "w+")
                        file.write(evaluation)
                        file.close()
                        await context.client.send_file(
                            context.chat_id,
                            "output.log",
                            reply_to=context.id,
                            caption="`Output exceeded limit, attaching file.`",
                        )
                        remove("output.log")
                        return
                    await context.edit(
                        f">>> {expression}\n"
                        f"{evaluation}"
                    )

        except Exception as err:
            await context.edit(
                f">>> {expression}\n"
                f"`{err}`"
            )

        if log:
            await context.client.send_message(
                log_chatid, f"Evaluated `{expression}` in the python interpreter."
            )


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

        if uid is 0:
            await context.edit(
                f"`{user}`@{hostname} ~"
                f"\n> `#` {command}"
            )
        else:
            await context.edit(
                f"`{user}`@{hostname} ~"
                f"\n> `$` {command}"
            )

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=PIPE,
            stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if result:
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
        else:
            return
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
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            if result:
                if len(result) > 4096:
                    await context.edit("`Output exceeded limit, attaching file.`")
                    file = open("output.log", "w+")
                    file.write(result)
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
                    f"{result}"
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


@register(outgoing=True, pattern="^-shutdown$")
async def shutdown(context):
    """ To re-execute Jarvis. """
    if not context.text[0].isalpha():
        await context.edit("`Attempting re-execution.`")
        if log:
            await context.client.send_message(
                log_chatid,
                "Jarvis power off."
            )
        await context.client.disconnect()


command_help.update({
    "sh": "Parameter: -sh <command>\
    \nUsage: Executes a shell command."
})

command_help.update({
    "pip": "Parameter: -pip <module(s)>\
    \nUsage: Searches pip for the requested modules."
})

command_help.update({
    "shutdown": "Parameter: -shutdown\
    \nUsage: Shuts down Jarvis."
})
