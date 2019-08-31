""" Jarvis module for adding captions to image. """

from os import remove
from jarvis import command_help, log, log_chatid
from jarvis.events import register, diagnostics
from jarvis.utils import execute


@register(outgoing=True, pattern="^-caption(?: |$)(.*)")
@diagnostics
async def caption(context):
    """ Generates images with captions. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.fwd_from:
            return
        reply = await context.get_reply_message()
        reply_id = None
        await context.edit("`Generating meme, please wait . . .`")
        if reply:
            reply_id = reply.id
            target_file_path = await context.client.download_media(
                await context.get_reply_message()
            )
        else:
            target_file_path = await context.download_media()
        if ',' in context.pattern_match.group(1):
            string_1, string_2 = context.pattern_match.group(1).split(',', 1)
        else:
            string_1 = context.pattern_match.group(1)
            string_2 = " "
        if target_file_path is None:
            await context.edit("`There are no attachment in target.`")
            return
        result = await execute("./utils/meme.sh \"" + target_file_path +
                               "\" meme.png" + " \"" + str(string_1) +
                               "\" " + "\"" + str(string_2) + "\"")
        if not result:
            await context.edit("`Something wrong happened, please report this problem.`")
            try:
                remove("meme.png")
                remove(target_file_path)
            except FileNotFoundError:
                pass
            return
        try:
            await context.client.send_file(
                context.chat_id,
                "meme.png",
                reply_to=reply_id
            )
        except ValueError:
            await context.edit("`An error occurred during the conversion.`")
            remove(target_file_path)
            return
        await context.delete()
        remove("meme.png")
        remove(target_file_path)
        message = string_1 + "` and `" + string_2
        if log:
            await context.client.send_message(
                log_chatid, "Captions `" + message + "` added to an image."
            )
command_help.update({
    "caption": "Parameter: -caption <text>,<text> <image>\
    \nUsage: Adds two lines of captions to an image."
})
