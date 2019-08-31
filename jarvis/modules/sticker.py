""" Module to add an image/sticker into your pack. """

from urllib import request
from io import BytesIO
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
from jarvis import bot, command_help
from jarvis.events import register, diagnostics
from jarvis.utils import resize_photo


# noinspection PyUnusedLocal
@register(outgoing=True, pattern="^-sticker")
@diagnostics
async def sticker(context):
    """ Fetches images/stickers and add them to your pack. """
    emoji = None
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        user = await bot.get_me()
        if not user.username:
            user.username = user.first_name
        message = await context.get_reply_message()
        emojibypass = False
        if message and message.media:
            if isinstance(message.media, MessageMediaPhoto):
                photo = BytesIO()
                photo = await bot.download_media(message.photo, photo)
            elif "image" in message.media.document.mime_type.split('/'):
                photo = BytesIO()
                await bot.download_file(message.media.document, photo)
                if (DocumentAttributeFilename(file_name='sticker.webp')
                        in message.media.document.attributes):
                    emoji = message.media.document.attributes[1].alt
                    emojibypass = True
            else:
                await context.edit("`This file type is not supported.`")
                return
        else:
            await context.edit("`Please reply to a message with an image/sticker.`")
            return
        if photo:
            await context.edit("Collecting sticker . . .")
            image = await resize_photo(photo)
            splat = context.text.split()
            if not emojibypass:
                emoji = "👀"
            pack = "1"
            if len(splat) == 3:
                pack = splat[2]
                emoji = splat[1]
            elif len(splat) == 2:
                if splat[1].isnumeric():
                    pack = int(splat[1])
                else:
                    emoji = splat[1]
            packname = f"pack_{user.id}_{user.username}"
            response = request.urlopen(
                request.Request(f'http://t.me/addstickers/{packname}')
            )
            htmlstr = response.read().decode("utf8").split('\n')
            file = BytesIO()
            file.name = "sticker.png"
            image.save(file, "PNG")
            if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in htmlstr:
                async with bot.conversation('Stickers') as conv:
                    await conv.send_message('/addsticker')
                    await conv.get_response()
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.send_message(packname)
                    await conv.get_response()
                    file.seek(0)
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.send_file(file, force_document=True)
                    await conv.get_response()
                    await conv.send_message(emoji)
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await conv.send_message('/done')
                    await conv.get_response()
                    await bot.send_read_acknowledge(conv.chat_id)
            else:
                await context.edit("Pack not found, creating pack . . .")
                async with bot.conversation('Stickers') as conv:
                    await conv.send_message('/newpack')
                    await conv.get_response()
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.send_message(f"@{user.username}'s pack")
                    await conv.get_response()
                    await bot.send_read_acknowledge(conv.chat_id)
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                    await conv.get_response()
                    await conv.send_message(emoji)
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await conv.send_message("/publish")
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await conv.send_message("/skip")
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await conv.send_message(packname)
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await bot.send_read_acknowledge(conv.chat_id)

            await context.edit(
                f"Sticker has been added to [this](t.me/addstickers/{packname}) pack.",
                parse_mode='md'
            )
command_help.update({
    "sticker": "Parameter: -sticker <emoji>\
    \nUsage: Collects image/sticker as sticker, specify emoji to set custom emoji."
})
