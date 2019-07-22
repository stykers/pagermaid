""" QR Code related utilities. """

import os
import pyqrcode

from jarvis import command_help, log, log_chatid
from jarvis.events import register
from pyzbar.pyzbar import decode
from PIL import Image


@register(pattern=r"-genqr(?: |$)([\s\S]*)", outgoing=True)
async def genqr(context):
    """ Generate QR codes. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.fwd_from:
            return
        input_string = context.pattern_match.group(1)
        message = None
        result = None
        if input_string:
            message = input_string
        elif context.reply_to_msg_id:
            reply = await context.get_reply_message()
            result = reply.id
            if reply.media:
                downloaded_file_name = await context.client.download_media(
                    reply
                )
                with open(downloaded_file_name, "rb") as file:
                    lines = file.readlines()
                message = ""
                for media in lines:
                    try:
                        message += media.decode("UTF-8") + "\n"
                    except UnicodeDecodeError:
                        await context.edit("`Unable to parse file as plaintext.`")
                        os.remove(downloaded_file_name)
                        return
                os.remove(downloaded_file_name)
            else:
                message = reply.message
        if message is None:
            await context.edit("`Invalid argument.`")
            return
        await context.edit("`Generating QR code.`")
        try:
            pyqrcode.create(message, error='L', mode='binary').png('qr.webp', scale=6)
        except UnicodeEncodeError:
            await context.edit("`Invalid characters in target string.`")
            os.remove(downloaded_file_name)
            return
        await context.client.send_file(
            context.chat_id,
            "qr.webp",
            reply_to=result
        )
        os.remove("qr.webp")
        await context.delete()
        if log:
            await context.client.send_message(
                log_chatid, "Generated QR code for `" + message + "`."
            )
        await context.delete()


@register(pattern=r"^-parseqr$", outgoing=True)
async def parseqr(context):
    """ Parse QR code into plaintext. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.fwd_from:
            return
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
        try:
            try:
                message = str(decode(Image.open(target_file_path))[0].data)[2:][:-1]
                await context.edit("Content: `" + message + "`.")
                success = True
            except IndexError:
                await context.edit("`Target is not a QR code.`")
                success = False
                message = None
            os.remove(target_file_path)
        except AttributeError:
            await context.edit("`Invalid argument.`")
            return
        if success:
            if log:
                await context.client.send_message(
                    log_chatid, "Parsed QR code with content `" + message + "`."
                )
        else:
            if log:
                await context.client.send_message(
                    log_chatid, "Attempted to parse non-encoded image as QR code."
                )

command_help.update({
    "genqr": "Parameter: -genqr <text>\
    \nUsage: Generates a QR code sticker."
})

command_help.update({
    "parseqr": "Parameter: -parseqr\
    \nUsage: Parse the attached QR code into plaintext."
})
