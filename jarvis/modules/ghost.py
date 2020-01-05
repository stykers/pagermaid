""" Ghost a user by sending read to every single message they send. """

from jarvis import redis, redis_check, command_help, log, log_chatid
from jarvis.events import register, diagnostics


@register(outgoing=True, pattern="^-ghost_enable$")
@diagnostics
async def ghost_enable(context):
    """ Enables ghosting of a user. """
    if not redis_check():
        await context.edit("Redis is offline, cannot operate.")
        return
    redis.set("ghosted.chat_id." + str(context.chat_id), "true")
    await context.delete()
    if log:
        await context.client.send_message(
            log_chatid,
            "UserID " + str(context.chat_id) + " added to list of ghosted users.")


@register(outgoing=True, pattern="^-ghost_disable$")
@diagnostics
async def ghost_disable(context):
    """ Disables ghosting of a user. """
    if not redis_check():
        await context.edit("Redis is offline, cannot operate.")
        return
    redis.delete("ghosted.chat_id." + str(context.chat_id))
    await context.delete()
    if log:
        await context.client.send_message(
            log_chatid,
            "UserID " + str(context.chat_id) + " removed from list of ghosted users.")
command_help.update({
    "ghost_disable": "Parameter: -ghost_disable\
    \nUsage: Disables ghosting of a user."
})


@register(incoming=True, disable_edited=True)
async def set_read_acknowledgement(context):
    """ Event handler to infinitely mute ghosted users. """
    if not redis_check():
        return
    if redis.get("ghosted.chat_id." + str(context.chat_id)):
        await context.client.send_read_acknowledge(context.chat_id)
