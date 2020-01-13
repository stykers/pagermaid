""" PagerMaid module for different ways to avoid users. """

from pagermaid import redis, redis_check, command_help, log, log_chatid
from pagermaid.listener import listener, diagnostics


@listener(outgoing=True, command="ghost")
@diagnostics
async def ghost(context):
    """ Toggles ghosting of a user. """
    if not redis_check():
        await context.edit("Redis is offline, cannot operate.")
        return
    if context.pattern_match.group(1) == 'true':
        redis.set("ghosted.chat_id." + str(context.chat_id), "true")
        await context.delete()
        if log:
            await context.client.send_message(
                log_chatid,
                "ChatID " + str(context.chat_id) + " added to ghosted chats.")
    elif context.pattern_match.group(1) == 'false':
        redis.delete("ghosted.chat_id." + str(context.chat_id))
        await context.delete()
        if log:
            await context.client.send_message(
                log_chatid,
                "ChatID " + str(context.chat_id) + " removed from ghosted chats.")
    elif context.pattern_match.group(1) == 'status':
        if redis.get("ghosted.chat_id." + str(context.chat_id)):
            await context.edit("Current chat is ghosted.")
        else:
            await context.edit("Current chat is not ghosted.")
    else:
        await context.edit("Invalid argument.")


command_help.update({
    "ghost": "Parameter: -ghost <true|false|status>\
    \nUsage: Toggles ghosting of chat, requires redis."
})


@listener(outgoing=True, command="deny")
@diagnostics
async def deny(context):
    """ Toggles denying of a user. """
    if not redis_check():
        await context.edit("Redis is offline, cannot operate.")
        return
    if context.pattern_match.group(1) == 'true':
        redis.set("denied.chat_id." + str(context.chat_id), "true")
        await context.delete()
        if log:
            await context.client.send_message(
                log_chatid,
                "ChatID " + str(context.chat_id) + " added to denied chats.")
    elif context.pattern_match.group(1) == 'false':
        redis.delete("denied.chat_id." + str(context.chat_id))
        await context.delete()
        if log:
            await context.client.send_message(
                log_chatid,
                "ChatID " + str(context.chat_id) + " removed from denied chats.")
    elif context.pattern_match.group(1) == 'status':
        if redis.get("silenced.chat_id." + str(context.chat_id)):
            await context.edit("Current chat is denied.")
        else:
            await context.edit("Current chat is not denied.")
    else:
        await context.edit("Invalid argument.")


command_help.update({
    "deny": "Parameter: -deny <true|false|status>\
    \nUsage: Toggles denying of chat, requires redis."
})


@listener(incoming=True, ignore_edited=True)
async def set_read_acknowledgement(context):
    """ Event handler to infinitely read ghosted messages. """
    if not redis_check():
        return
    if redis.get("ghosted.chat_id." + str(context.chat_id)):
        await context.client.send_read_acknowledge(context.chat_id)


@listener(incoming=True, ignore_edited=True)
async def message_removal(context):
    """ Event handler to infinitely delete denied messages. """
    if not redis_check():
        return
    if redis.get("denied.chat_id." + str(context.chat_id)):
        await context.delete()
