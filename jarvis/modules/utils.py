""" Useful utilities for Jarvis. """
import speedtest
import os

from datetime import datetime
from telethon import functions
from jarvis import command_help, log, log_chatid
from jarvis.events import register
from emoji import get_emoji_regexp
from googletrans import LANGUAGES
from googletrans import Translator
from os import remove
from gtts import gTTS
from dotenv import load_dotenv


load_dotenv("config.env")
lang = os.environ.get("APPLICATION_LANGUAGE", "en")


@register(outgoing=True, pattern="^-shutdown$")
async def shutdown(context):
    """ To re-execute Jarvis. """
    if not context.text[0].isalpha():
        await context.edit("`Attempting re-execution.`")
        if log:
            await context.client.send_message(
                log_chatid,
                "Jarvis power off."
            )
        await context.client.disconnect()


@register(outgoing=True, pattern="^-channel$")
async def channel(context):
    """ Returns the author's channel. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Author Channel: @SparkzStuff")


@register(outgoing=True, pattern="^-source$")
async def source(context):
    """ Prints the git repository URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://git.stykers.moe/scm/~stykers/jarvis.git")


@register(outgoing=True, pattern="^-site$")
async def site(context):
    """ Outputs the site URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://jarvis.stykers.moe/")


@register(outgoing=True, pattern="^-speed$")
async def speed(context):
    """ Tests internet speed using speedtest. """
    global result
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("`Executing test scripts . . .`")
        test = speedtest.Speedtest()

        test.get_best_server()
        test.download()
        test.upload()
        test.results.share()
        result = test.results.dict()

    await context.edit("Timestamp "
                       f"`{result['timestamp']}` \n\n"
                       "Upload "
                       f"`{unit_convert(result['upload'])}` \n"
                       "Download "
                       f"`{unit_convert(result['download'])}` \n"
                       "Latency "
                       f"`{result['ping']}` \n"
                       "ISP "
                       f"`{result['client']['isp']}`")


@register(outgoing=True, pattern="^-connection$")
async def connection(context):
    """ Shows connection info. """
    datacenter = await context.client(functions.help.GetNearestDcRequest())
    await context.edit(
        f"Region `{datacenter.country}` \n"
        f"Connected Datacenter `{datacenter.this_dc}` \n"
        f"Nearest Datacenter `{datacenter.nearest_dc}`"
    )


@register(outgoing=True, pattern="^-ping$")
async def ping(context):
    """ Calculates the latency of the bot host. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        start = datetime.now()
        await context.edit("`Pong!`")
        end = datetime.now()
        duration = (end - start).microseconds / 1000
        await context.edit("`Pong!|%sms`" % duration)


def unit_convert(byte):
    """ Converts byte into readable formats. """
    power = 2 ** 10
    zero = 0
    units = {
        0: '',
        1: 'Kb/s',
        2: 'Mb/s',
        3: 'Gb/s',
        4: 'Tb/s'}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"


@register(outgoing=True, pattern=r"^-translate(?: |$)([\s\S]*)")
async def translate(context):
    """ Jarvis universal translator. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        translator = Translator()
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid parameter.`")
            return

        try:
            await context.edit("`Generating translation . . .`")
            reply_text = translator.translate(clear_emojis(message), dest=lang)
        except ValueError:
            await context.edit("`Language not found, please correct the error in the config file.`")
            return

        source_lang = LANGUAGES[f'{reply_text.src.lower()}']
        trans_lang = LANGUAGES[f'{reply_text.dest.lower()}']
        reply_text = f"**Translated** from {source_lang.title()}:\n{reply_text.text}"

        if len(reply_text) > 4096:
            await context.edit("`Output exceeded limit, attaching file.`")
            file = open("output.log", "w+")
            file.write(reply_text)
            file.close()
            await context.client.send_file(
                context.chat_id,
                "output.log",
                reply_to=context.id,
            )
            remove("output.log")
            return
        await context.edit(reply_text)
        if log:
            log_message = f"Translated `{message}` from {source_lang} to {trans_lang}."
            if len(log_message) > 4096:
                await context.edit("`Output exceeded limit, attaching file.`")
                file = open("output.log", "w+")
                file.write(log_message)
                file.close()
                await context.client.send_file(
                    context.chat_id,
                    "output.log",
                    reply_to=context.id,
                )
                remove("output.log")
                return
            await context.client.send_message(
                log_chatid,
                log_message,
            )


@register(outgoing=True, pattern=r"^-tts(?: |$)([\s\S]*)")
async def tts(context):
    """ Send TTS stuff as voice message. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid argument.`")
            return

        try:
            await context.edit("`Generating vocals . . .`")
            gTTS(message, lang)
        except AssertionError:
            await context.edit("`Invalid argument.`")
            return
        except ValueError:
            await context.edit('`Language not found, please correct the error in the config file.`')
            return
        except RuntimeError:
            await context.edit('`Error loading array of languages.`')
            return
        gtts = gTTS(message, lang)
        gtts.save("vocals.mp3")
        with open("vocals.mp3", "rb") as audio:
            line_list = list(audio)
            line_count = len(line_list)
        if line_count == 1:
            gtts = gTTS(message, lang)
            gtts.save("vocals.mp3")
        with open("vocals.mp3", "r"):
            await context.client.send_file(context.chat_id, "vocals.mp3", voice_note=True)
            remove("vocals.mp3")
            if log:
                await context.client.send_message(
                    log_chatid, "Generated tts for `" + message + "`."
                )
            await context.delete()


def clear_emojis(target):
    """ Removes all Emojis from provided string """
    return get_emoji_regexp().sub(u'', target)


command_help.update({
    "shutdown": "Parameter: -shutdown\
    \nUsage: Shuts down Jarvis."
})
command_help.update({
    "channel": "Parameter: -channel\
    \nUsage: Shows the development channel."
})
command_help.update({
    "source": "Parameter: -source\
    \nUsage: Prints the git repository URL."
})

command_help.update({
    "site": "Parameter: -site\
    \nUsage: Shows the site of Jarvis."
})
command_help.update({
    "speed": "Parameter: -speed\
    \nUsage: Execute the speedtest script and outputs your internet speed."
})

command_help.update({
    "connection": "Parameter: -connection\
    \nUsage: Shows your connection info."
})

command_help.update({
    "ping": "Parameter: -ping\
    \nUsage: Outputs your latency to telegram."
})

command_help.update({
    "translate": "Parameter: -translate <text>\
    \nUsage: Translate the target message into English."
})

command_help.update({
    "tts": "Parameter: -tts <text>\
    \nUsage: Generates a voice message."
})
