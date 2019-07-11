""" Useful utils in group chats. """

from time import sleep
from telethon.tl.functions.channels import LeaveChannelRequest
from jarvis import command_help, bot, log, log_chatid
from jarvis.events import register


@register(outgoing=True, pattern="^-userid$")
async def userid(target):
    """ Queries the userid of a user. """
    if not target.text[0].isalpha() and target.text[0] not in ("/", "#", "@", "!"):
        message = await target.get_reply_message()
        if message:
            if not message.forward:
                user_id = message.sender.id
                if message.sender.username:
                    name = "@" + message.sender.username
                else:
                    name = "**" + message.sender.first_name + "**"

            else:
                user_id = message.forward.sender.id
                if message.forward.sender.username:
                    name = "@" + message.forward.sender.username
                else:
                    name = "*" + message.forward.sender.first_name + "*"
            await target.edit(
                "**Username:** {} \n**UserID:** `{}`"
                .format(name, user_id)
            )


@register(outgoing=True, pattern="^-chatid$")
async def chatid(chat):
    """ Queries the chatid of the chat you are in. """
    if not chat.text[0].isalpha() and chat.text[0] not in ("/", "#", "@", "!"):
        await chat.edit("ChatID: `" + str(chat.chat_id) + "`")


@register(outgoing=True, pattern=r"^-log(?: |$)([\s\S]*)")
async def log(log_text):
    """ Forwards a message into log group """
    if not log_text.text[0].isalpha() and log_text.text[0] not in ("/", "#", "@", "!"):
        if log:
            if log_text.reply_to_msg_id:
                reply_msg = await log_text.get_reply_message()
                await reply_msg.forward_to(log_chatid)
            elif log_text.pattern_match.group(1):
                user = f"#LOG / Chat ID: {log_text.chat_id}\n\n"
                text = user + log_text.pattern_match.group(1)
                await bot.send_message(log_chatid, text)
            else:
                await log_text.edit("`Specify target message.`")
                return
            await log_text.edit("Noted.")
        else:
            await log_text.edit("`Logging is disabled.`")


@register(outgoing=True, pattern="^-leave$")
async def leave(context):
    """ It leaves you from the group. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Goodbye.")
        await bot(LeaveChannelRequest(leave.chat_id))


@register(outgoing=True, pattern="^-shutdown$")
async def shutdown(context):
    """ To shutdown Jarvis. """
    if not context.text[0].isalpha():
        await context.edit("`Jarvis is powering off.`")
        if log:
            await context.client.send_message(
                log_chatid,
                "Jarvis power off."
            )
        await context.client.disconnect()


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
command_help.update({
    "shutdown": "Parameter: -shutdown\
    \nUsage: Shuts down Jarvis."
})
