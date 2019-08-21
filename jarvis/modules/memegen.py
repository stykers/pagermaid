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
            await context.edit("`An error occurred during the conversion.`")
            remove(target_file_path)
            return
        await context.delete()
        remove("meme.png")
        remove(target_file_path)
        message = string_1 + "` and `" + string_2
        if log:
            await context.client.send_message(
                log_chatid, "Meme generated with text `" + message + "`."
            )
command_help.update({
    "meme": "Parameter: -meme <image> <text>,<text>\
    \nUsage: Generates a meme image with specified image and text."
})
