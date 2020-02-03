""" QR Code related utilities. """

from os import remove
from pyqrcode import create
from pyzbar.pyzbar import decode
from PIL import Image
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import obtain_message, upload_attachment


@listener(outgoing=True, command="genqr",
          description="Generates a QR Code sticker from a specific string.",
          parameters="<string>")
async def genqr(context):
    """ Generate QR codes. """
    reply_id = context.reply_to_msg_id
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("Invalid argument.")
        return
    await context.edit("Generating QR code.")
    try:
        create(message, error='L', mode='binary').png('qr.webp', scale=6)
    except UnicodeEncodeError:
        await context.edit("Invalid characters in target string.")
        return
    await upload_attachment("qr.webp", context.chat_id, reply_id)
    remove("qr.webp")
    await context.delete()
    await log(f"Generated QR Code for `{message}`.")


@listener(outgoing=True, command="parseqr",
          description="Parse attachment of replied message as a QR Code and output results.")
async def parseqr(context):
    """ Parse attachment of replied message as a QR Code and output results. """
    success = False
    target_file_path = await context.client.download_media(
        await context.get_reply_message()
    )
    if not target_file_path:
        await context.edit("There are no attachments in the message.")
        return
    try:
        message = str(decode(Image.open(target_file_path))[0].data)[2:][:-1]
        success = True
        await context.edit(f"**Content: **\n"
                           f"`{message}`")
    except IndexError:
        await context.edit("Target is not a QR Code.")
        message = None
    if success:
        await log(f"Parsed QR Code with content `{message}`.")
    remove(target_file_path)
