""" System related utilities for PagerMaid to integrate into the system. """

from platform import node
from getpass import getuser
from os import geteuid
from requests import head
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import attach_log, execute


@listener(outgoing=True, command="sh",
          description="Use the command-line from Telegram.",
          parameters="<command>")
async def sh(context):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = context.arguments
    hostname = node()
    if context.is_channel and not context.is_group:
        await context.edit("`Current configuration disables shell execution in channel.`")
        return

    if not command:
        await context.edit("`Invalid argument.`")
        return

    if geteuid() == 0:
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
            await attach_log(result, context.chat_id, "output.log", context.id)
            return

        if geteuid() == 0:
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
    url = context.arguments
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
                await attach_log(result, context.chat_id, "output.log", context.id)
                return
            await context.edit(
                "Redirects:\n"
                f"{result}"
            )
            await log(f"Traced redirects of {context.arguments}.")
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
    await context.edit("`A conversation have been opened, click `[here](tg://user?id=503691334)` to enter.`",
                       parse_mode="markdown")
    message = "Hi, I would like to report something about PagerMaid."
    if context.arguments:
        message = context.arguments
    await context.client.send_message(
        503691334,
        message
    )


def url_tracer(url):
    """ Method to trace URL redirects. """
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
