""" Jarvis regex utility. """

import re

from sre_constants import error as sre_err
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from jarvis.events import register

deliminators = ("/", ":", "|", "_")


@register(outgoing=True, pattern="^s")
async def sed(context):
    """ Implements regex on telegram. """
    result = format_sed(context.text)
    target = await context.get_reply_message()
    if result:
        if target:
            message = target.text
        else:
            await context.edit(
                "`Unable to retrieve target data.`"
            )
            return

        reply, reply_result, flags = result

        if not reply:
            await context.edit(
                "`Unable to retrieve target data.`"
            )
            return

        try:
            check = re.match(reply, message, flags=re.IGNORECASE)
            if check and check.group(0).lower() == message.lower():
                await context.edit(
                    "`Invalid argument.`"
                )
                return

            if "i" in flags and "g" in flags:
                text = re.sub(reply, reply_result, message, flags=re.I).strip()
            elif "i" in flags:
                text = re.sub(reply, reply_result, message,
                              count=1, flags=re.I).strip()
            elif "g" in flags:
                text = re.sub(reply, reply_result, message).strip()
            else:
                text = re.sub(reply, reply_result, message, count=1).strip()
        except sre_err:
            await context.edit("`Syntax error in pattern.`")
            return
        if text:
            if target.sender.is_self:
                try:
                    await target.edit(text)
                except MessageNotModifiedError:
                    await context.delete()
                    return
                await context.delete()
            else:
                await context.edit("*" + text + "\n\n Pattern: \"" + context.text + "\"")


def format_sed(data):
    """ Separate sed arguments. """
    try:
        if (
                len(data) >= 1 and
                data[1] in deliminators and
                data.count(data[1]) >= 2
        ):
            target = data[1]
            start = counter = 2
            while counter < len(data):
                if data[counter] == "\\":
                    counter += 1

                elif data[counter] == target:
                    replace = data[start:counter]
                    counter += 1
                    start = counter
                    break

                counter += 1

            else:
                return None

            while counter < len(data):
                if (
                        data[counter] == "\\" and
                        counter + 1 < len(data) and
                        data[counter + 1] == target
                ):
                    data = data[:counter] + data[counter + 1:]

                elif data[counter] == target:
                    replace_with = data[start:counter]
                    counter += 1
                    break

                counter += 1
            else:
                return replace, data[start:], ""

            flags = ""
            if counter < len(data):
                flags = data[counter:]
            return replace, replace_with, flags.lower()
        return None
    except IndexError:
        pass
