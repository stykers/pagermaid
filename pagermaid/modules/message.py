""" Message related utilities. """

from telethon.tl.functions.messages import DeleteChatUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.errors.rpcerrorlist import ChatIdInvalidError, PeerIdInvalidError
from pagermaid import command_help, bot, log, log_chatid
from pagermaid.listener import listener, diagnostics
from pagermaid.utils import random_gen


@listener(outgoing=True, command="userid")
@diagnostics
async def userid(context):
    """ Queries the userid of a user. """
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
            "**Username:** {} \n**UserID:** `{}`"
                .format(target, user_id)
        )
    else:
        await context.edit("`Unable to get the target message.`")


command_help.update({
    "userid": "Parameter: -userid\
    \nUsage: Query the userid of the sender of the message you replied to."
})


@listener(outgoing=True, command="chatid")
@diagnostics
async def chatid(context):
    """ Queries the chatid of the chat you are in. """
    await context.edit("ChatID: `" + str(context.chat_id) + "`")


command_help.update({
    "chatid": "Parameter: -chatid\
    \nUsage: Query the chatid of the chat you are in"
})


@listener(outgoing=True, command="log")
@diagnostics
async def log(context):
    """ Forwards a message into log group """
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


command_help.update({
    "log": "Parameter: -log <text>\
    \nUsage: Forwards a message or log some text."
})


@listener(outgoing=True, command="leave")
@diagnostics
async def leave(context):
    """ It leaves you from the group. """
    await context.edit("Wasted my time, bye.")
    try:
        await bot(DeleteChatUserRequest(chat_id=context.chat_id,
                                        user_id=context.sender_id
                                        ))
    except ChatIdInvalidError:
        await bot(LeaveChannelRequest(chatid))
    except PeerIdInvalidError:
        await context.edit("You are not in a group.")


command_help.update({
    "leave": "Parameter: -leave\
    \nUsage: Say goodbye and leave."
})


@listener(outgoing=True, command="rng")
@diagnostics
async def rng(context):
    """ Automates keyboard spamming. """
    await random_gen(context, "A-Za-z0-9")


command_help.update({
    "rng": "Parameter: -rng <integer>\
    \nUsage: Automates keyboard spamming."
})


@listener(outgoing=True, command="meter2feet")
@diagnostics
async def meter2feet(context):
    """ Converts meter to feet. """
    meter = float(context.pattern_match.group(1))
    feet = meter / .3048
    await context.edit("Converted " + str(meter) + " meters to " + str(feet) + " feet.")


command_help.update({
    "meter2feet": "Parameter: -meter2feet <float>\
    \nUsage: Converts meter to feet."
})


@listener(outgoing=True, command="feet2meter")
@diagnostics
async def feet2meter(context):
    """ Converts feet to meter. """
    feet = float(context.pattern_match.group(1))
    meter = feet * .3048
    await context.edit("Converted " + str(feet) + " feet to " + str(meter) + " meter.")


command_help.update({
    "feet2meter": "Parameter: -feet2meter <float>\
    \nUsage: Converts feet to meter."
})


@listener(outgoing=True, command="source")
@diagnostics
async def source(context):
    """ Prints the git repository URL. """
    await context.edit("https://git.stykers.moe/scm/~stykers/pagermaid.git")


command_help.update({
    "source": "Parameter: -source\
    \nUsage: Prints the git repository URL."
})


@listener(outgoing=True, command="site")
@diagnostics
async def site(context):
    """ Outputs the site URL. """
    await context.edit("https://katonkeyboard.moe/pagermaid.html")


command_help.update({
    "site": "Parameter: -site\
    \nUsage: Shows the site of PagerMaid."
})
