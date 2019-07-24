""" Jarvis auto-response for when you are AFK. """
import time

from telethon.events import StopPropagation
from jarvis import log, log_chatid, command_help, count_msg, users, redis_check
from jarvis.events import register
from jarvis.modules.database import afk_reason, is_afk, not_afk
from jarvis.modules.database import afk as db_afk


@register(outgoing=True, pattern="^-afk")
async def afk(context):
    """ To set yourself as afk. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if not redis_check():
            await context.edit("`The database is malfunctioning.`")
            return
        message = context.text
        try:
            reason = str(message[5:])
        except:
            reason = ''
        if not reason:
            reason = 'rest'
        await context.edit("Gotta go.")
        if log:
            await context.client.send_message(log_chatid, "User is afk, begin message logging.")
        await db_afk(reason)
        raise StopPropagation


@register(outgoing=True)
async def back(context):
    if not redis_check():
        return
    afk_query = await is_afk()
    if afk_query is True:
        await not_afk()
        if log:
            await context.client.send_message(
                log_chatid,
                "You received " +
                str(count_msg) +
                " messages from " +
                str(len(users)) +
                " groups while afk.",
            )
            for i in users:
                name = await context.client.get_entity(i)
                name0 = str(name.first_name)
                await context.client.send_message(
                    log_chatid,
                    "[" +
                    name0 +
                    "](tg://user?id=" +
                    str(i) +
                    ")" +
                    " messaged/mentioned you " +
                    "`" +
                    str(users[i]) +
                    " times.`",
                )


@register(incoming=True, disable_edited=True)
async def mention_respond(context):
    """ Auto-respond to mentions. """
    global count_msg
    if not redis_check():
        return
    query_afk = await is_afk()
    if context.message.mentioned and not (await context.get_sender()).bot:
        if query_afk is True:
            if context.sender_id not in users:
                await context.reply(
                    "**Jarvis Auto Respond**\n"
                    + "`I am away for "
                    + await afk_reason()
                    + ", your message is logged.`"
                )
                users.update({context.sender_id: 1})
                count_msg = count_msg + 1
            elif context.sender_id in users:
                if users[context.sender_id] % 5 == 0:
                    await context.reply(
                        "Jarvis Auto Respond\n"
                        + "`Sorry, I am still away for "
                        + await afk_reason()
                        + ", your message priority is upgraded.`"
                    )
                    users[context.sender_id] = users[context.sender_id] + 1
                    count_msg = count_msg + 1
                else:
                    users[context.sender_id] = users[context.sender_id] + 1
                    count_msg = count_msg + 1


@register(incoming=True)
async def afk_on_pm(context):
    global count_msg
    if not redis_check():
        return
    query_afk = await is_afk()
    if context.is_private and not (await context.get_sender()).bot:
        if query_afk is True:
            if context.sender_id not in users:
                await context.reply(
                    "Jarvis Auto Respond\n"
                    + "`I am away for "
                    + await afk_reason()
                    + ", your message is logged.`"
                )
                users.update({context.sender_id: 1})
                count_msg = count_msg + 1
            elif context.sender_id in users:
                if users[context.sender_id] % 5 == 0:
                    await context.reply(
                        "Jarvis Auto Respond\n"
                        + "`Sorry, I am still away for "
                        + await afk_reason()
                        + ", your message priority is upgraded.`"
                    )
                    users[context.sender_id] = users[context.sender_id] + 1
                    count_msg = count_msg + 1
                else:
                    users[context.sender_id] = users[context.sender_id] + 1
                    count_msg = count_msg + 1


command_help.update({
    "afk": "Parameter: -afk <text>\
    \nUsage: Sets yourself to afk and enables message logging and auto response, a message cancels the status."
})
