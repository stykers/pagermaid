""" Message related utilities. """

from telethon.tl.functions.messages import DeleteChatUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.errors.rpcerrorlist import ChatIdInvalidError
from distutils2.util import strtobool
from pagermaid import bot, log, config
from pagermaid.listener import listener


@listener(outgoing=True, command="userid",
          description="Query the UserID of the sender of the message you replied to.")
async def userid(context):
    """ Query the UserID of the sender of the message you replied to. """
    message = await context.get_reply_message()
    if message:
        if not message.forward:
            user_id = message.sender.id
            if message.sender.username:
                target = "@" + message.sender.username
            else:
                try:
                    target = "**" + message.sender.first_name + "**"
                except TypeError:
                    target = "**" + "Deleted Account" + "**"

        else:
            user_id = message.forward.sender.id
            if message.forward.sender.username:
                target = "@" + message.forward.sender.username
            else:
                target = "*" + message.forward.sender.first_name + "*"
        await context.edit(
            f"**Username:** {target} \n"
            f"**UserID:** `{user_id}`"
        )
    else:
        await context.edit("Unable to fetch information of target message.")


@listener(outgoing=True, command="chatid",
          description="Query the chatid of the chat the command was executing in.")
async def chatid(context):
    """ Queries the chatid of the chat you are in. """
    await context.edit("ChatID: `" + str(context.chat_id) + "`")


@listener(outgoing=True, command="log",
          description="Forwards a message or a string.",
          parameters="<string>")
async def log(context):
    """ Forwards a message into log group """
    if strtobool(config['log']):
        if context.reply_to_msg_id:
            reply_msg = await context.get_reply_message()
            await reply_msg.forward_to(int(config['log_chatid']))
        elif context.arguments:
            await log(context.arguments)
        else:
            await context.edit("Invalid argument.")
            return
        await context.edit("Noted.")
    else:
        await context.edit("Logging is disabled.")


@listener(outgoing=True, command="leave",
          description="Say goodbye and leave.")
async def leave(context):
    """ It leaves you from the group. """
    if context.is_group:
        await context.edit("Wasted my time, bye.")
        try:
            await bot(DeleteChatUserRequest(chat_id=context.chat_id,
                                            user_id=context.sender_id
                                            ))
        except ChatIdInvalidError:
            await bot(LeaveChannelRequest(chatid))
    else:
        await context.edit("Current chat is not a group chat.")


@listener(outgoing=True, command="meter2feet",
          description="Convert meters to feet.",
          parameters="<meters>")
async def meter2feet(context):
    """ Convert meter to feet. """
    if not len(context.parameter) == 1:
        await context.edit("Invalid argument.")
        return
    meter = float(context.parameter[0])
    feet = meter / .3048
    await context.edit(f"Converted {str(meter)} meters to {str(feet)} feet.")


@listener(outgoing=True, command="feet2meter",
          description="Convert feet to meters.",
          parameters="<feet>")
async def feet2meter(context):
    """ Convert feet to meter. """
    if not len(context.parameter) == 1:
        await context.edit("Invalid argument.")
        return
    feet = float(context.parameter[0])
    meter = feet * .3048
    await context.edit(f"Converted {str(feet)} feet to {str(meter)} meter.")


@listener(outgoing=True, command="source",
          description="Shows URL of PagerMaid git repository.")
async def source(context):
    """ Outputs the git repository URL. """
    await context.edit("https://git.stykers.moe/scm/~stykers/pagermaid.git")


@listener(outgoing=True, command="site",
          description="Shows URL of PagerMaid project homepage.")
async def site(context):
    """ Outputs the site URL. """
    await context.edit("https://katonkeyboard.moe/pagermaid.html")
