""" PagerMaid module for adding captions to image. """

from os import remove
from pygments import highlight as syntax_highlight
from pygments.formatters import img
from pygments.lexers import guess_lexer
from pagermaid import command_help, log, log_chatid
from pagermaid.listener import listener, diagnostics
from pagermaid.utils import execute, obtain_source_file, upload_result_image


@listener(outgoing=True, command="convert")
@diagnostics
async def convert(context):
    """ Converts image to png. """
    try:
        reply_id, target_file_path = await obtain_source_file(context)
    except ValueError:
        return
    result = await execute("./utils/caption.sh \"" + target_file_path +
                           "\" result.png" + " \"" + str("") +
                           "\" " + "\"" + str("") + "\"")
    if not result:
        await context.edit("`Something wrong happened, please report this problem.`")
        try:
            remove("result.png")
            remove(target_file_path)
        except FileNotFoundError:
            pass
        return
    try:
        await context.client.send_file(
            context.chat_id,
            "result.png",
            reply_to=reply_id
        )
    except ValueError:
        await context.edit("`An error occurred during the conversion.`")
        remove(target_file_path)
        return
    await context.delete()
    remove(target_file_path)
    remove("result.png")


command_help.update({
    "convert": "Parameter: -convert <image>\
    \nUsage: Converts any image to png."
})


@listener(outgoing=True, command="caption")
@diagnostics
async def caption(context):
    """ Generates images with captions. """
    if context.pattern_match.group(1):
        if ',' in context.pattern_match.group(1):
            string_1, string_2 = context.pattern_match.group(1).split(',', 1)
        else:
            string_1 = context.pattern_match.group(1)
            string_2 = " "
    else:
        await context.edit("Invalid syntax.")
        return
    try:
        reply_id, target_file_path = await obtain_source_file(context)
    except ValueError:
        return
    result = await execute("./utils/caption.sh \"" + target_file_path +
                           "\" result.png" + " \"" + str(string_1) +
                           "\" " + "\"" + str(string_2) + "\"")
    try:
        await upload_result_image(context, result, target_file_path, reply_id)
    except ValueError:
        return
    message = string_1 + "` and `" + string_2
    if log:
        await context.client.send_message(
            log_chatid, "Captions `" + message + "` added to an image."
        )


command_help.update({
    "caption": "Parameter: -caption <text>,<text> <image>\
    \nUsage: Adds two lines of captions to an image."
})


@listener(outgoing=True, command="ocr")
@diagnostics
async def ocr(context):
    """ Extracts texts from images. """
    if context.fwd_from:
        return
    reply = await context.get_reply_message()
    await context.edit("`Processing image, please wait . . .`")
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    else:
        target_file_path = await context.download_media()
    if target_file_path is None:
        await context.edit("`There are no attachment in target.`")
        return
    result = await execute(f"tesseract {target_file_path} stdout")
    if not result:
        await context.edit("`Something wrong happened, please report this problem.`")
        try:
            remove(target_file_path)
        except FileNotFoundError:
            pass
        return
    success = False
    if result == "/bin/sh: fbdump: command not found":
        await context.edit("A utility is missing.")
    else:
        result = await execute(f"tesseract {target_file_path} stdout", False)
        await context.edit(f"**Extracted text: **\n{result}")
        success = True
    remove(target_file_path)
    if not success:
        return
    if log:
        await context.client.send_message(
            log_chatid, "Performed OCR on an image."
        )


command_help.update({
    "ocr": "Parameter: -ocr <image>\
    \nUsage: Extracts texts from images."
})


@listener(outgoing=True, command="highlight")
@diagnostics
async def highlight(context):
    """ Generates syntax highlighted images. """
    if context.fwd_from:
        return
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("Rendering image, please wait . . .")
    if reply:
        reply_id = reply.id
        message = reply.text
    else:
        if context.pattern_match.group(1):
            message = context.pattern_match.group(1)
        else:
            await context.edit("`Unable to retrieve target message.`")
            return
    lexer = guess_lexer(message)
    formatter = img.JpgImageFormatter(style="colorful")
    result = syntax_highlight(message, lexer, formatter, outfile=None)
    await context.edit("Uploading image . . .")
    await context.client.send_file(
        context.chat_id,
        result,
        reply_to=reply_id
    )
    await context.delete()


command_help.update({
    "highlight": "Parameter: -highlight <image>\
    \nUsage: Generates syntax highlighted images."
})
