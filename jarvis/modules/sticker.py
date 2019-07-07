""" Module to add an image/sticker into your pack. """

import io
import math

from urllib import request
from PIL import Image
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
from jarvis import bot, command_help
from jarvis.events import register


@register(outgoing=True, pattern="^s!sticker")
async def sticker(args):
    """ Fetches images/stickers and add them to your pack. """
    global emoji
    if not args.text[0].isalpha() and args.text[0] not in ("/", "#", "@", "!"):
        user = await bot.get_me()
        if not user.username:
            user.username = user.first_name
        message = await args.get_reply_message()
        photo = None
        emojibypass = False
        if message and message.media:
            if isinstance(message.media, MessageMediaPhoto):
                photo = io.BytesIO()
                photo = await bot.download_media(message.photo, photo)
            elif "image" in message.media.document.mime_type.split('/'):
                photo = io.BytesIO()
                await bot.download_file(message.media.document, photo)
                if (DocumentAttributeFilename(file_name='sticker.webp')
                        in message.media.document.attributes):
                    emoji = message.media.document.attributes[1].alt
                    emojibypass = True
            else:
                await args.edit("`This file type is not supported.`")
                return
        else:
            await args.edit("`Please reply to a message with an image/sticker.`")
            return
        if photo:
            image = await resize_photo(photo)
            splat = args.text.split()
            if not emojibypass:
                emoji = "🤔"
            pack = "1"
            if len(splat) == 3:
                pack = splat[2]
                emoji = splat[1]
            elif len(splat) == 2:
                if splat[1].isnumeric():
                    pack = int(splat[1])
                else:
                    emoji = splat[1]
            packname = f"{user.id}_{user.username}_{pack}"
            response = request.urlopen(
                request.Request(f'http://t.me/addstickers/{packname}')
            )
            htmlstr = response.read().decode("utf8").split('\n')
            file = io.BytesIO()
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
                await args.edit("Pack not found, creating pack.")
                async with bot.conversation('Stickers') as conv:
                    await conv.send_message('/newpack')
                    await conv.get_response()
                    await bot.send_read_acknowledge(conv.chat_id)
                    await conv.send_message(f"@{user.username}'s pack.")
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

            await args.edit(
                f"Sticker has been added to [this](t.me/addstickers/{packname}) pack.",
                parse_mode='md'
            )


async def resize_photo(photo):
    """ Photo resize to match sticker standards. """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512/size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512/size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


command_help.update({
    "sticker": "Parameter: s!sticker\
\nUsage: Reply s!sticker to a sticker or an image to crop and add it to your pack.\
\n\nParameter: s!sticker [emoji(s)]\
\nWorks just like s!sticker but uses the emoji(s) in the parameter.\
\n\nParameter: s!sticker [id]\
\nUsage: Adds the sticker to the specified pack but uses 🤔 as emoji."
})

