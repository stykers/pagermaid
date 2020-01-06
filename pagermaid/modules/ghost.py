""" Ghost a user by sending read to every single message they send. """

from pagermaid import redis, redis_check, command_help, log, log_chatid
from pagermaid.events import register, diagnostics


@register(outgoing=True, pattern="^^-ghost(?: |$)(.*)")
@diagnostics
async def ghost_enable(context):
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
                "ChatID " + str(context.chat_id) + " added to list of ghosted users.")
    elif context.pattern_match.group(1) == 'false':
        redis.delete("ghosted.chat_id." + str(context.chat_id))
        await context.delete()
        if log:
            await context.client.send_message(
                log_chatid,
                "ChatID " + str(context.chat_id) + " removed from list of ghosted users.")
    else:
        await context.edit("Invalid argument.")


command_help.update({
    "ghost": "Parameter: -ghost <true|false>\
    \nUsage: Toggles ghosting of user, requires redis."
})


@register(incoming=True, disable_edited=True)
async def set_read_acknowledgement(context):
    """ Event handler to infinitely mute ghosted users. """
    if not redis_check():
        return
    if redis.get("ghosted.chat_id." + str(context.chat_id)):
        await context.client.send_read_acknowledge(context.chat_id)
