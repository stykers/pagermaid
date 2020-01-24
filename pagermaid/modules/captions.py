""" PagerMaid module for adding captions to image. """

from os import remove
from pygments import highlight as syntax_highlight
from pygments.formatters import img
from pygments.lexers import guess_lexer
from pagermaid import log, working_dir
from pagermaid.listener import listener
from pagermaid.utils import execute, obtain_source_file, upload_result_image


@listener(outgoing=True, command="convert",
          description="Converts attachment of replied message to png.")
async def convert(context):
    """ Converts image to png. """
    try:
        reply_id, target_file_path = await obtain_source_file(context)
    except ValueError:
        return
    result = await execute(f"{working_dir}/assets/caption.sh \"" + target_file_path +
                           "\" result.png" + " \"" + str("") +
                           "\" " + "\"" + str("") + "\"")
    if not result:
        await context.edit("Something wrong happened, please report this problem.")
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
        await context.edit("An error occurred during the conversion.")
        remove(target_file_path)
        return
    await context.delete()
    remove(target_file_path)
    remove("result.png")


@listener(outgoing=True, command="caption",
          description="Adds two lines of captions to attached image of replied message, separated by a comma.",
          parameters="<string>,<string> <image>")
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
    result = await execute(f"{working_dir}/assets/caption.sh \"{target_file_path}\" "
                           f"{working_dir}/assets/Impact-Regular.ttf "
                           f"\"{str(string_1)}\" \"{str(string_2)}\"")
    try:
        await upload_result_image(context, result, target_file_path, reply_id)
    except ValueError:
        return
    if string_2 != " ":
        message = string_1 + "` and `" + string_2
    else:
        message = string_1
    await log(f"Caption `{message}` added to an image.")


@listener(outgoing=True, command="ocr",
          description="Extract text from attached image of replied message.")
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


@listener(outgoing=True, command="highlight",
          description="Generates syntax highlighted images.",
          parameters="<string>")
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
