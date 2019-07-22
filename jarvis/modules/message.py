""" Message related utilities. """

from telethon import functions
from jarvis import command_help, bot, log, log_chatid
from jarvis.events import register


@register(outgoing=True, pattern="^-userid$")
async def userid(context):
    """ Queries the userid of a user. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        message = await context.get_reply_message()
        if message:
            if not message.forward:
                user_id = message.sender.id
                if message.sender.username:
                    target = "@" + message.sender.username
                else:
                    target = "**" + message.sender.first_name + "**"

            else:
                user_id = message.forward.sender.id
                if message.forward.sender.username:
                    target = "@" + message.forward.sender.username
                else:
                    target = "*" + message.forward.sender.first_name + "*"
            await context.edit(
                "**Username:** {} \n**UserID:** `{}`"
                .format(target, user_id)
            )
        else:
            await context.edit("`Unable to get the target message.`")


@register(outgoing=True, pattern="^-chatid$")
async def chatid(context):
    """ Queries the chatid of the chat you are in. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("ChatID: `" + str(context.chat_id) + "`")


@register(outgoing=True, pattern=r"^-log(?: |$)([\s\S]*)")
async def log(context):
    """ Forwards a message into log group """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if log:
            if context.reply_to_msg_id:
                reply_msg = await context.get_reply_message()
                await reply_msg.forward_to(log_chatid)
            elif context.pattern_match.group(1):
                user = f"Chat ID: {context.chat_id}\n\n"
                text = user + context.pattern_match.group(1)
                await bot.send_message(log_chatid, text)
            else:
                await context.edit("`Unable to get the target message.`")
                return
            await context.edit("Noted.")
        else:
            await context.edit("`Logging is disabled.`")


@register(outgoing=True, pattern="^-leave$")
async def leave(context):
    """ It leaves you from the group. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Goodbye.")
        try:
            await bot(functions.channels.LeaveChannelRequest(leave.chat_id))
        except AttributeError:
            await context.edit("You are not in a group.")


command_help.update({
    "chatid": "Parameter: -chatid\
    \nUsage: Query the chatid of the chat you are in"
})

command_help.update({
    "userid": "Parameter: -userid\
    \nUsage: Query the userid of the sender of the message you replied to."
})

command_help.update({
    "log": "Parameter: -log\
    \nUsage: Forwards message to logging group."
})

command_help.update({
    "leave": "Parameter: -leave\
    \nUsage: Say goodbye and leave."
})
