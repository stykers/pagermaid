""" Jarvis module to semi-automate moderation of a group. """

from asyncio import sleep
from telethon.errors import PhotoCropSizeSmallError, ImageProcessFailedError, ChatAdminRequiredError
from telethon.tl.types import MessageMediaPhoto, ChannelParticipantsAdmins
from telethon.tl.functions.channels import EditPhotoRequest
from jarvis import command_help, log, log_chatid, bot, redis_check
from jarvis.events import register


@register(outgoing=True, pattern="^-group_image$")
async def group_image(context):
    """ Sets image of a group. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        reply_msg = await context.get_reply_message()
        chat = await context.get_chat()
        photo = None

        if not chat.admin_rights or chat.creator:
            await context.edit("`Lacking permissions to edit group image.`")
            return

        if reply_msg and reply_msg.media:
            if isinstance(reply_msg.media, MessageMediaPhoto):
                photo = await bot.download_media(message=reply_msg.photo)
            elif "image" in reply_msg.media.document.mime_type.split('/'):
                photo = await bot.download_file(reply_msg.media.document)
            else:
                await context.edit("`Unable to parse attachment.`")

        if photo:
            try:
                EditPhotoRequest(
                    context.chat_id,
                    await bot.upload_file(photo)
                )
                await context.edit("`Group image updated.`")

            except PhotoCropSizeSmallError:
                await context.edit("`Image dimensions smaller than minimum requirements.`")
            except ImageProcessFailedError:
                await context.edit("`Failed to process image.`")
command_help.update({
    "group_image": "Parameter: -group_image <image>\
    \nUsage: Changes the group's pfp to the attachment."
})


@register(outgoing=True, pattern="^-admins$")
async def admins(context):
    """ Lists admins of the group chat. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if not context.is_group:
            await context.edit("Current chat is not a group.")
            return
        info = await context.client.get_entity(context.chat_id)
        title = info.title if info.title else "this chat"
        result = f"**Admin list of {title}:** \n"
        try:
            async for user in context.client.iter_participants(
                    context.chat_id, filter=ChannelParticipantsAdmins
            ):
                if not user.deleted:
                    url = "[{}](tg://user?id={})"
                    try:
                        link = url.format(user.first_name + " " + user.last_name, user.id)
                    except TypeError:
                        link = url.format(user.first_name, user.id)
                    user_id = f"{user.id}"
                    result += f"\n{link}<{user_id}>"
                else:
                    result += f"\nDeleted Account<{user.id}>"
        except ChatAdminRequiredError as err:
            result += " " + str(err) + "\n"
        await context.edit(result)
command_help.update({
    "admins": "Parameter: -admins\
    \nUsage: Lists admins in the group."
})
