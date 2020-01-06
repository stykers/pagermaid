""" PagerMaid features that uses external HTTP APIs other than Telegram. """

from googletrans import Translator, LANGUAGES
from os import remove, environ
from dotenv import load_dotenv
from gtts import gTTS
from pagermaid import command_help, log, log_chatid
from pagermaid.events import register, diagnostics
from pagermaid.utils import clear_emojis, attach_log, GoogleSearch

load_dotenv("config.env")
lang = environ.get("APPLICATION_LANGUAGE", "en")
result_length = environ.get("RESULT_LENGTH", 5)


@register(outgoing=True, pattern=r"^-translate(?: |$)([\s\S]*)")
@diagnostics
async def translate(context):
    """ PagerMaid universal translator. """
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
        result = translator.translate(clear_emojis(message), dest=lang)
    except ValueError:
        await context.edit("`Language not found, please correct the error in the config file.`")
        return

    source_lang = LANGUAGES[f'{result.src.lower()}']
    trans_lang = LANGUAGES[f'{result.dest.lower()}']
    result = f"**Translated** from {source_lang.title()}:\n{result.text}"

    if len(result) > 4096:
        await context.edit("`Output exceeded limit, attaching file.`")
        await attach_log(context, result)
        return
    await context.edit(result)
    if log:
        result = f"Translated `{message}` from {source_lang} to {trans_lang}."
        if len(result) > 4096:
            await context.edit("`Output exceeded limit, attaching file.`")
            await attach_log(context, result)
            return
        await context.client.send_message(
            log_chatid,
            result,
        )


command_help.update({
    "translate": "Parameter: -translate <text>\
    \nUsage: Translate the target message into English."
})


@register(outgoing=True, pattern=r"^-tts(?: |$)([\s\S]*)")
@diagnostics
async def tts(context):
    """ Send TTS stuff as voice message. """
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


command_help.update({
    "tts": "Parameter: -tts <text>\
    \nUsage: Generates a voice message."
})


@register(outgoing=True, pattern=r"^-google(?: |$)([\s\S]*)")
@diagnostics
async def google(context):
    """ Searches Google for a string. """
    query = context.pattern_match.group(1)
    await context.edit("Pulling results . . .")
    search_results = GoogleSearch().search(query=query)
    results = ""
    count = 0
    for result in search_results.results:
        if count == result_length:
            break
        count += 1
        title = result.title
        link = result.url
        desc = result.text
        results += f"\n[{title}]({link}) \n`{desc}`\n"
    await context.edit(f"**Google** |`{query}`| 🎙 🔍 \n"
                       f"{results}",
                       link_preview=False)
    if log:
        await context.client.send_message(
            log_chatid,
            "Queried `" + query + "` on Google Search.",
        )


command_help.update({
    "google": "Parameter: -google <text>\
    \nUsage: Searches Google for a string."
})