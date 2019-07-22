""" QR Code related utilities. """

import os
import pyqrcode

from jarvis import command_help, log, log_chatid
from jarvis.events import register


@register(pattern=r"-gen_qr(?: |$)([\s\S]*)", outgoing=True)
async def gen_qr(context):
    """ Generate QR codes. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.fwd_from:
            return
        input_string = context.pattern_match.group(1)
        message = "`Invalid argument.`"
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
                    m_list = file.readlines()
                message = ""
                for media in m_list:
                    message += media.decode("UTF-8") + "\r\n"
                os.remove(downloaded_file_name)
            else:
                message = reply.message
        await context.edit("`Generating QR code.`")
        pyqrcode.create(message, error='L', mode='binary').png('qr.webp', scale=6)
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


command_help.update({
    "gen_qr": "Parameter: -gen_qr <text>\
    \nUsage: Generates a QR code sticker."
})
