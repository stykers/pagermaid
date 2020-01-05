""" PagerMaid regex utility. """

from sre_constants import error as sre_err
from re import match, sub, I, IGNORECASE
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from pagermaid.events import register, diagnostics
from pagermaid.utils import format_sed


@register(outgoing=True, pattern="^s")
@diagnostics
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
            check = match(reply, message, flags=IGNORECASE)
            if check and check.group(0).lower() == message.lower():
                await context.edit(
                    "`Invalid argument.`"
                )
                return

            if "i" in flags and "g" in flags:
                text = sub(reply, reply_result, message, flags=I).strip()
            elif "i" in flags:
                text = sub(reply, reply_result, message,
                           count=1, flags=I).strip()
            elif "g" in flags:
                text = sub(reply, reply_result, message).strip()
            else:
                text = sub(reply, reply_result, message, count=1).strip()
        except sre_err:
            await context.edit("`Syntax error in pattern.`")
            return
        if text:
            if not context.message.sender.is_self:
                await context.client.send_message(context.chat_id,
                                                  "*" + text + "\n\n Pattern: \"" + context.text + "\"")
                return
            if target.sender.is_self:
                try:
                    await target.edit(text)
                except MessageNotModifiedError:
                    await context.delete()
                    return
                await context.delete()
            else:
                await context.edit("*" + text + "\n\n Pattern: \"" + context.text + "\"")
