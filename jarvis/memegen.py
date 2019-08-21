""" Jarvis module for generating memes. """

from os import remove
from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from jarvis import command_help, log, log_chatid
from jarvis.events import register


@register(pattern=r"^-meme(?: |$)([\s\S]*)", outgoing=True)
async def meme(context):
    """ Generates the meme. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.fwd_from:
            return
        reply = await context.get_reply_message()
        result = reply.id
        input_string = context.pattern_match.group(1)
        string_1, string_2 = context.pattern_match.group(1).split(',', 1)
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
        command = "./utils/meme.sh \"" + \
                  target_file_path + \
                  "\" meme.png" + \
                  "\"" + \
                  string_1 + \
                  "\"" + \
                  "\"" + \
                  string_2 + \
                  "\""
        execute = await async_run(
            command,
            stdout=PIPE,
            stderr=PIPE
        )

        stdout, stderr = await execute.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())
        try:
            try:
                await context.client.send_file(
                    context.chat_id,
                    "meme.png",
                    reply_to=result
                )
                await context.delete()
                success = True
                message = "Here's the generated meme."
            except IndexError:
                await context.edit("`Target is not a valid image.`")
                success = False
                message = None
            remove(target_file_path)
            remove("meme.png")
        except AttributeError:
            await context.edit("`Invalid argument.`")
            return
        if success:
            if log:
                await context.client.send_message(
                    log_chatid, "Meme generated with text `" + message + "`."
                )
        else:
            if log:
                await context.client.send_message(
                    log_chatid, "Attempted to generate meme without success."
                )
command_help.update({
    "meme": "Parameter: -meme <image> <text>\
    \nUsage: Generates a meme with specified image and text."
})
