""" Jarvis module for generating memes. """

from os import remove
from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from jarvis import command_help, log, log_chatid
from jarvis.events import register


@register(outgoing=True, pattern="^-meme(?: |$)(.*)")
async def meme(context):
    """ Generates the meme. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if context.fwd_from:
            return
        reply = await context.get_reply_message()
        reply_id = None
        target_file_path = None
        if reply:
            reply_id = reply.id
            target_file_path = await context.client.download_media(
                await context.get_reply_message()
            )
        else:
            target_file_path = await context.download_media()
        string_1, string_2 = context.pattern_match.group(1).split(',', 1)
        await context.edit("`Generating meme, please wait . . .`")
        command = "./utils/meme.sh \"" + \
                  target_file_path + \
                  "\" meme.png" + \
                  " \"" + \
                  str(string_1) + \
                  "\" " + \
                  "\"" + \
                  str(string_2) + \
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
            await context.client.send_file(
                context.chat_id,
                "meme.png",
                reply_to=reply_id
            )
        except ValueError:
            await context.edit("`Unsupported image type.`")
            remove(target_file_path)
        await context.delete()
        remove("meme.png")
        remove(target_file_path)
        message = string_1 + "` and `" + string_2
        if log:
            await context.client.send_message(
                log_chatid, "Meme generated with text `" + message + "`."
            )
command_help.update({
    "meme": "Parameter: -meme <image> <text>\
    \nUsage: Generates a meme with specified image and text."
})
