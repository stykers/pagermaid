""" QR Code related utilities. """

from os import remove
from pyqrcode import create
from pyzbar.pyzbar import decode
from PIL import Image
from pagermaid import log
from pagermaid.listener import listener


@listener(outgoing=True, command="genqr",
          description="Generates a QR Code sticker from a specific string.",
          parameters="<string>")
async def genqr(context):
    """ Generate QR codes. """
    downloaded_file_name = None
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
                    remove(downloaded_file_name)
                    return
            remove(downloaded_file_name)
        else:
            message = reply.message
    if message is None:
        await context.edit("`Invalid argument.`")
        return
    await context.edit("`Generating QR code.`")
    try:
        create(message, error='L', mode='binary').png('qr.webp', scale=6)
    except UnicodeEncodeError:
        await context.edit("`Invalid characters in target string.`")
        remove(downloaded_file_name)
        return
    await context.client.send_file(
        context.chat_id,
        "qr.webp",
        reply_to=result
    )
    remove("qr.webp")
    await context.delete()
    if len(message) <= 4096:
        await log(f"Generated QR Code for `{message}`.")
    else:
        await log("Generated QR Code for message.")
    await context.delete()


@listener(outgoing=True, command="parseqr",
          description="Parse attachment of replied message as a QR Code and output results.")
async def parseqr(context):
    """ Parse QR code into plaintext. """
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
        remove(target_file_path)
    except AttributeError:
        await context.edit("`Invalid argument.`")
        return
    if success:
        if len(message) <= 4096:
            await log(f"Parsed QR Code with content `{message}`.")
        else:
            await log("Parsed QR Code with content message.")
