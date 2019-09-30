""" Message related utilities. """

from os import environ
from googletrans import Translator, LANGUAGES
from os import remove
from gtts import gTTS
from dotenv import load_dotenv
from telethon.tl.functions.messages import DeleteChatUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.errors.rpcerrorlist import ChatIdInvalidError, PeerIdInvalidError
from jarvis import command_help, bot, log, log_chatid
from jarvis.events import register, diagnostics
from jarvis.utils import clear_emojis, attach_log, random_gen

load_dotenv("config.env")
lang = environ.get("APPLICATION_LANGUAGE", "en")


@register(outgoing=True, pattern="^-userid$")
@diagnostics
async def userid(context):
    """ Queries the userid of a user. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        message = await context.get_reply_message()
        if message:
            if not message.forward:
                user_id = message.sender.id
                if message.sender.username:
                    target = "@" + message.sender.username
                else:
                    try:
                        target = "**" + message.sender.first_name + "**"
                    except TypeError:
                        target = "**" + "Deleted Account" + "**"

            else:
                user_id = message.forward.sender.id
                if message.forward.sender.username:
                    target = "@" + message.forward.sender.username
                else:
                    target = "*" + message.forward.sender.first_name + "*"
            await context.edit(
                "**Username:** {} \n**UserID:** `{}`"
                .format(target, user_id)
            )
        else:
            await context.edit("`Unable to get the target message.`")
command_help.update({
    "userid": "Parameter: -userid\
    \nUsage: Query the userid of the sender of the message you replied to."
})


@register(outgoing=True, pattern="^-chatid$")
@diagnostics
async def chatid(context):
    """ Queries the chatid of the chat you are in. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("ChatID: `" + str(context.chat_id) + "`")
command_help.update({
    "chatid": "Parameter: -chatid\
    \nUsage: Query the chatid of the chat you are in"
})


@register(outgoing=True, pattern=r"^-log(?: |$)([\s\S]*)")
@diagnostics
async def log(context):
    """ Forwards a message into log group """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if log:
            if context.reply_to_msg_id:
                reply_msg = await context.get_reply_message()
                await reply_msg.forward_to(log_chatid)
            elif context.pattern_match.group(1):
                user = f"Chat ID: {context.chat_id}\n\n"
                text = user + context.pattern_match.group(1)
                await bot.send_message(log_chatid, text)
            else:
                await context.edit("`Unable to get the target message.`")
                return
            await context.edit("Noted.")
        else:
            await context.edit("`Logging is disabled.`")
command_help.update({
    "log": "Parameter: -log <text>\
    \nUsage: Forwards a message or log some text."
})


@register(outgoing=True, pattern="^-leave$")
@diagnostics
async def leave(context):
    """ It leaves you from the group. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Wasted my time, bye.")
        try:
            await bot(DeleteChatUserRequest(chat_id=context.chat_id,
                                            user_id=context.sender_id
                                            ))
        except ChatIdInvalidError:
            await bot(LeaveChannelRequest(chatid))
        except PeerIdInvalidError:
            await context.edit("You are not in a group.")
command_help.update({
    "leave": "Parameter: -leave\
    \nUsage: Say goodbye and leave."
})


@register(outgoing=True, pattern=r"^-translate(?: |$)([\s\S]*)")
@diagnostics
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
command_help.update({
    "tts": "Parameter: -tts <text>\
    \nUsage: Generates a voice message."
})


@register(outgoing=True, pattern="^-rng(?: |$)(.*)")
@diagnostics
async def rng(context):
    """ Automates keyboard spamming. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await random_gen(context, "A-Za-z0-9")
command_help.update({
    "rng": "Parameter: -rng <integer>\
    \nUsage: Automates keyboard spamming."
})


@register(outgoing=True, pattern="^-slepkat(?: |$)(.*)")
@diagnostics
async def slepkat(context):
    """ Sleepykat simulator. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await random_gen(context, "Zz")
command_help.update({
    "slepkat": "Parameter: -slepkat <integer>\
    \nUsage: Sleepykat simulator."
})


@register(outgoing=True, pattern="^-aaa(?: |$)(.*)")
@diagnostics
async def aaa(context):
    """ Generates screams. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await random_gen(context, "Aa")
command_help.update({
    "aaa": "Parameter: -aaa <integer>\
    \nUsage: Generates screams."
})


@register(outgoing=True, pattern="^-meter2feet(?: |$)(.*)")
@diagnostics
async def meter2feet(context):
    """ Converts meter to feet. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        meter = float(context.pattern_match.group(1))
        feet = meter / .3048
        await context.edit("Converted " + str(meter) + " meters to " + str(feet) + " feet.")
command_help.update({
    "meter2feet": "Parameter: -meter2feet <float>\
    \nUsage: Converts meter to feet."
})


@register(outgoing=True, pattern="^-feet2meter(?: |$)(.*)")
@diagnostics
async def feet2meter(context):
    """ Converts feet to meter. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        feet = float(context.pattern_match.group(1))
        meter = feet * .3048
        await context.edit("Converted " + str(feet) + " feet to " + str(meter) + " meter.")
command_help.update({
    "feet2meter": "Parameter: -feet2meter <float>\
    \nUsage: Converts feet to meter."
})


@register(outgoing=True, pattern="^-source$")
@diagnostics
async def source(context):
    """ Prints the git repository URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://git.stykers.moe/scm/~stykers/jarvis.git")
command_help.update({
    "source": "Parameter: -source\
    \nUsage: Prints the git repository URL."
})


@register(outgoing=True, pattern="^-site$")
@diagnostics
async def site(context):
    """ Outputs the site URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://jarvis.stykers.moe/")
command_help.update({
    "site": "Parameter: -site\
    \nUsage: Shows the site of Jarvis."
})
