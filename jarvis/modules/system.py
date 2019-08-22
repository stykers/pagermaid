""" System related utilities for Jarvis to integrate into the system. """

import asyncio
import platform

from requests import head
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
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
command_help.update({
    "evaluate": "Parameter: -evaluate <expression>>\
    \nUsage: Evaluate an expression in the python interpreter."
})


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
command_help.update({
    "sh": "Parameter: -sh <command>\
    \nUsage: Executes a shell command."
})


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
                    await attach_log(context, result)
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
command_help.update({
    "pip": "Parameter: -pip <module(s)>\
    \nUsage: Searches pip for the requested modules."
})


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
    "shutdown": "Parameter: -shutdown\
    \nUsage: Shuts down Jarvis."
})


@register(outgoing=True, pattern="^-trace(?: |$)(.*)")
async def trace(context):
    """ Trace URL redirects. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        url = context.pattern_match.group(1)
        reply = await context.get_reply_message()
        if reply:
            url = reply.text
        if url:
            if url.startswith("https://") or url.startswith("http://"):
                pass
            else:
                url = "https://" + url
            await context.edit("`Tracing redirects . . .`")
            result = str("")
            for url in url_tracer(url):
                count = 0
                if result:
                    result += " ↴\n" + url
                else:
                    result = url
                if count == 128:
                    result += "\n\nMore than 128 redirects, aborting!"
                    break
            if result:
                if len(result) > 4096:
                    await context.edit("`Output exceeded limit, attaching file.`")
                    await attach_log(context, result)
                    return
                await context.edit(
                    "Redirects:\n"
                    f"{result}"
                )
            else:
                await context.edit(
                    "`Something wrong happened while making HTTP requests.`"
                )
        else:
            await context.edit("`Invalid argument.`")
command_help.update({
    "trace": "Parameter: -trace <url>\
    \nUsage: Traces redirect of a URL."
})


@register(outgoing=True, pattern="^-contact(?: |$)(.*)")
async def contact(context):
    """ To contact the creator of Jarvis. """
    if not context.text[0].isalpha():
        await context.edit("`A conversation have been opened, click `[here](tg://user?id=503691334)` to enter.`",
                           parse_mode="markdown")
        message = "Hi, I have encountered a problem with Jarvis."
        if context.pattern_match.group(1):
            message = context.pattern_match.group(1)
        await context.client.send_message(
            "503691334",
            message
        )
command_help.update({
    "contact": "Parameter: -contact <message>\
    \nUsage: Contact the author."
})


def url_tracer(url):
    while True:
        yield url
        try:
            response = head(url)
        except MissingSchema:
            break
        except InvalidURL:
            break
        except ConnectionError:
            break
        if 300 < response.status_code < 400:
            url = response.headers['location']
        else:
            break


async def attach_log(context, result):
    file = open("output.log", "w+")
    file.write(result)
    file.close()
    await context.client.send_file(
        context.chat_id,
        "output.log",
        reply_to=context.id,
    )
    remove("output.log")
