""" System related utilities for PagerMaid to integrate into the system. """

from platform import node
from getpass import getuser
from os import remove
from os import geteuid
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import url_tracer, attach_log, execute


@listener(outgoing=True, command="evaluate",
          description="Evaluate an expression in the python interpreter.",
          parameters="<expression>")
async def evaluate(context):
    """ Evaluate a python expression. """
    if context.pattern_match.group(1):
        expression = context.pattern_match.group(1)
    else:
        await context.edit("Invalid parameter.")
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
                        caption="Output exceeded limit, attaching file.",
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

    await log(f"Evaluated `{expression}` in the python interpreter.")


@listener(outgoing=True, command="sh",
          description="Use the command-line from Telegram.",
          parameters="<command>")
async def sh(context):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = context.pattern_match.group(1)
    uid = geteuid()
    hostname = node()
    if context.is_channel and not context.is_group:
        await context.edit("`Current configuration disables shell execution in channel.`")
        return

    if not command:
        await context.edit("`Invalid argument.`")
        return

    if uid == 0:
        await context.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `#` {command}"
        )
    else:
        await context.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `$` {command}"
        )

    result = await execute(command)

    if result:
        if len(result) > 4096:
            await attach_log(context, result)
            return

        if uid == 0:
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
    await log(f"Command `{command}` executed in the shell.")


@listener(outgoing=True, command="restart", diagnostics=False,
          description="Triggers system restart of PagerMaid.")
async def restart(context):
    """ To re-execute PagerMaid. """
    if not context.text[0].isalpha():
        await context.edit("Attempting system restart.")
        await log("PagerMaid restarted.")
        await context.client.disconnect()


@listener(outgoing=True, command="trace",
          description="Trace redirects of a URL.",
          parameters="<url>")
async def trace(context):
    """ Trace URL redirects. """
    url = context.pattern_match.group(1)
    reply = await context.get_reply_message()
    if reply:
        url = reply.text
    if url:
        if url.startswith("https://") or url.startswith("http://"):
            pass
        else:
            url = "https://" + url
        await context.edit("Tracing redirects . . .")
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
                await context.edit("Output exceeded limit, attaching file.")
                await attach_log(context, result)
                return
            await context.edit(
                "Redirects:\n"
                f"{result}"
            )
            await log(f"Traced redirects of {context.pattern_match.group(1)}.")
        else:
            await context.edit(
                "Something wrong happened while making HTTP requests."
            )
    else:
        await context.edit("Invalid argument.")


@listener(outgoing=True, command="contact",
          description="Sends a message to Kat.",
          parameters="<message>")
async def contact(context):
    """ Sends a message to Kat. """
    if not context.text[0].isalpha():
        await context.edit("`A conversation have been opened, click `[here](tg://user?id=503691334)` to enter.`",
                           parse_mode="markdown")
        message = "Hi, I would like to report something about PagerMaid."
        if context.pattern_match.group(1):
            message = context.pattern_match.group(1)
        await context.client.send_message(
            503691334,
            message
        )
