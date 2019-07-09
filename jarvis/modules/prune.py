""" Module to automate message deletion. """

from asyncio import sleep
from telethon.errors import rpcbaseerrors
from jarvis import log, log_chatid, command_help
from jarvis.events import register


@register(outgoing=True, pattern="^.prune$")
async def prune(message):
    """ Purge every single message after the message you replied to. """
    if not message.text[0].isalpha() and message.text[0] not in ("/", "#", "@", "!"):
        chat = await message.get_input_chat()
        msgs = []
        count = 0

        async for msg in message.client.iter_messages(chat, min_id=message.reply_to_msg_id):
            msgs.append(msg)
            count = count + 1
            msgs.append(message.reply_to_msg_id)
            if len(msgs) == 100:
                await message.client.delete_messages(chat, msgs)
                msgs = []

        if msgs:
            await message.client.delete_messages(chat, msgs)
        notify = await message.client.send_message(
            message.chat_id,
            "Deleted "
            + str(count)
            + " messages.",
        )

        if log:
            await message.client.send_message(
                log_chatid, "Deleted " +
                str(count) + " messages."
            )
        await sleep(3)
        await notify.delete()
