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
