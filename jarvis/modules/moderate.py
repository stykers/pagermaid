""" Jarvis module to semi-automate moderation of a group. """

from asyncio import sleep
from telethon.errors import PhotoCropSizeSmallError, ImageProcessFailedError
from telethon.tl.types import MessageMediaPhoto
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
