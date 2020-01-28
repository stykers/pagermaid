""" Module to automate message deletion. """

from asyncio import sleep
from telethon.errors.rpcbaseerrors import BadRequestError
from pagermaid import log
from pagermaid.listener import listener


@listener(outgoing=True, command="prune",
          description="Deletes everything starting from the message you replied to.")
async def prune(context):
    """ Purge every single message after the message you replied to. """
    if not context.reply_to_msg_id:
        await context.edit("There are no message that are replied to.")
        return
    input_chat = await context.get_input_chat()
    messages = []
    count = 0
    async for message in context.client.iter_messages(input_chat, min_id=context.reply_to_msg_id):
        messages.append(message)
        count += 1
        messages.append(context.reply_to_msg_id)
        if len(messages) == 100:
            await context.client.delete_messages(input_chat, messages)
            messages = []

    if messages:
        await context.client.delete_messages(input_chat, messages)
    await log(f"Bulk deleted {str(count)} messages.")
    notification = await send_prune_notify(context, count)
    await sleep(.5)
    await notification.delete()


@listener(outgoing=True, command="selfprune",
          description="Deletes specific amount of messages you sent.",
          parameters="<integer>")
async def selfprune(context):
    """ Deletes specific amount of messages you sent. """
    if not len(context.parameter) == 1:
        await context.edit("Invalid argument.")
        return
    try:
        count = int(context.parameter[0])
    except ValueError:
        await context.edit("Invalid argument.")
        return
    count_buffer = 0
    async for message in context.client.iter_messages(context.chat_id, from_user="me"):
        if count_buffer == count:
            break
        await message.delete()
        count_buffer += 1
    await log(f"Bulk deleted {str(count)} messages sent by self.")
    notification = await send_prune_notify(context, count)
    await sleep(.5)
    await notification.delete()


@listener(outgoing=True, command="delete",
          description="Deletes the message you replied to.")
async def delete(context):
    """ Deletes the message you replied to. """
    target = await context.get_reply_message()
    if context.reply_to_msg_id:
        try:
            await target.delete()
            await context.delete()
            await log("Deleted a message.")
        except BadRequestError:
            await context.edit("Lacking permission to delete this message.")
    else:
        await context.delete()


async def send_prune_notify(context, count):
    return await context.client.send_message(
        context.chat_id,
        "Deleted "
        + str(count)
        + " messages."
    )
