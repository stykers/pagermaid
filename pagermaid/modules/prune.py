""" Module to automate message deletion. """

from asyncio import sleep
from telethon.errors.rpcbaseerrors import BadRequestError
from pagermaid import log
from pagermaid.listener import listener


@listener(outgoing=True, command="prune",
          description="Deletes everything starting from the message you replied to.")
async def prune(context):
    """ Purge every single message after the message you replied to. """
    try:
        chat = await context.get_input_chat()
        msgs = []
        count = 0

        async for msg in context.client.iter_messages(chat, min_id=context.reply_to_msg_id):
            msgs.append(msg)
            count = count + 1
            msgs.append(context.reply_to_msg_id)
            if len(msgs) == 100:
                await context.client.delete_messages(chat, msgs)
                msgs = []

        if msgs:
            await context.client.delete_messages(chat, msgs)
        notification = await send_prune_notify(context, count)
        await log(f"Deleted {str(count)} messages.")
        await sleep(0.5)
        await notification.delete()
    except TypeError:
        await context.edit("`Please reply to a message.`")


@listener(outgoing=True, command="selfprune",
          description="Deletes specific amount of messages you sent.",
          parameters="<integer>")
async def selfprune(context):
    """ Prune self message. """
    try:
        message = context.text
        count = int(message[11:])
        i = 1

        async for message in context.client.iter_messages(context.chat_id, from_user='me'):
            if i > count + 1:
                break
            i = i + 1
            await message.delete()

        notification = await send_prune_notify(context, count)
        await log(f"Deleted {str(count)} messages.")
        await sleep(0.5)
        await notification.delete()
    except ValueError:
        await context.edit("`Invalid parameter.`")


@listener(outgoing=True, command="delete",
          description="Deletes the message you replied to.")
async def delete(context):
    """ Deletes the replied message. """
    target = await context.get_reply_message()
    if context.reply_to_msg_id:
        try:
            await target.delete()
            await context.delete()
            await log("Deleted a message.")
        except BadRequestError:
            await context.edit("Lacking permission to delete this message.")


@listener(outgoing=True, command="timed",
          description="Creates a timed message that is deleted after the amount of time specified.",
          parameters="<time> <message>")
async def timed(context):
    """ A timed message that deletes itself. """
    try:
        message = context.text
        counter = int(message[7:9])
        text = str(context.text[9:])
        await context.delete()
        source_msg = await context.client.send_message(context.chat_id, text)
        await sleep(counter)
        await source_msg.delete()
        await log("Created timed message.")
    except ValueError:
        await context.edit("Invalid parameter.")


async def send_prune_notify(context, count):
    return await context.client.send_message(
        context.chat_id,
        "Deleted "
        + str(count)
        + " messages."
    )
