""" Libraries for python modules. """

from os import remove
from os.path import exists
from emoji import get_emoji_regexp
from random import random, randint, randrange, seed, choice
from json import load as load_json
from re import sub, IGNORECASE
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from youtube_dl import YoutubeDL
from pagermaid import working_dir, bot


async def upload_attachment(file_path, chat_id, reply_id, caption=None):
    if not exists(file_path):
        return False
    try:
        await bot.send_file(
            chat_id,
            file_path,
            reply_to=reply_id,
            caption=caption
        )
    except BaseException as exception:
        raise exception
    return True


async def fetch_youtube_audio(url, chat_id, reply_id):
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'outtmpl': "audio.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    YoutubeDL(youtube_dl_options).download([url])
    if not exists("audio.mp3"):
        return False
    await bot.send_file(
         chat_id,
         "audio.mp3",
         reply_to=reply_id
    )
    remove("audio.mp3")
    return True


async def execute(command, pass_error=True):
    executor = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        result = str(stdout.decode().strip()) \
                 + str(stderr.decode().strip())
    else:
        result = str(stdout.decode().strip())
    return result


async def random_gen(context, selection):
    try:
        length = context.pattern_match.group(1)
        if not length:
            length = 64
        result = await execute(f"head -c 65536 /dev/urandom | tr -dc {selection} | head -c {length} ; echo \'\'")
        await context.edit(result)
    except FileNotFoundError:
        await context.edit("`Kat didn't bring /usr/bin/head.`")


async def attach_log(plaintext, chat_id, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    await bot.send_file(
        chat_id,
        file_name,
        reply_to=reply_id,
        caption=caption
    )
    remove(file_name)


def owoifier(text):
    """ Converts your text to OwO """
    smileys = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω´・)', '(´・ω・`)']
    with open(f"{working_dir}/assets/replacements.json") as fp:
        replacements = load_json(fp)
    for expression in replacements:
        replacement = replacements[expression]
        text = sub(expression, replacement, text, flags=IGNORECASE)
    words = text.split()
    first_letter = words[0][0]
    letter_stutter = f"{first_letter}-{first_letter.lower()}-{first_letter.lower()}"
    if len(words[0]) > 1:
        words[0] = letter_stutter + words[0][1:]
    else:
        words[0] = letter_stutter
    text = " ".join(words)
    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')
    text = '! {}'.format(choice(smileys)).join(text.rsplit('!', 1))
    text = '? OwO'.join(text.rsplit('?', 1))
    text = '. {}'.format(choice(smileys)).join(text.rsplit('.', 1))
    text = f"{text} desu"
    for v in ['a', 'o', 'u', 'A', 'O', 'U']:
        if 'n{}'.format(v) in text:
            text = text.replace('n{}'.format(v), 'ny{}'.format(v))
        if 'N{}'.format(v) in text:
            text = text.replace('N{}'.format(v), 'N{}{}'.format('Y' if v.isupper() else 'y', v))
    return text


def mocker(text, diversity_bias=0.5, random_seed=None):
    """ Randomizes case in a string. """
    if diversity_bias < 0 or diversity_bias > 1:
        raise ValueError('diversity_bias must be between the inclusive range [0,1]')
    seed(random_seed)
    out = ''
    last_was_upper = True
    swap_chance = 0.5
    for c in text:
        if c.isalpha():
            if random() < swap_chance:
                last_was_upper = not last_was_upper
                swap_chance = 0.5
            c = c.upper() if last_was_upper else c.lower()
            swap_chance += (1 - swap_chance) * diversity_bias
        out += c
    return out


def corrupt(text):
    """ Summons fox to scratch strings. """
    num_accents_up = (1, 3)
    num_accents_down = (1, 3)
    num_accents_middle = (1, 2)
    max_accents_per_letter = 3
    dd = ['̖', ' ̗', ' ̘', ' ̙', ' ̜', ' ̝', ' ̞', ' ̟', ' ̠', ' ̤', ' ̥', ' ̦', ' ̩', ' ̪', ' ̫', ' ̬', ' ̭', ' ̮',
          ' ̯', ' ̰', ' ̱', ' ̲', ' ̳', ' ̹', ' ̺', ' ̻', ' ̼', ' ͅ', ' ͇', ' ͈', ' ͉', ' ͍', ' ͎', ' ͓', ' ͔', ' ͕',
          ' ͖', ' ͙', ' ͚', ' ', ]
    du = [' ̍', ' ̎', ' ̄', ' ̅', ' ̿', ' ̑', ' ̆', ' ̐', ' ͒', ' ͗', ' ͑', ' ̇', ' ̈', ' ̊', ' ͂', ' ̓', ' ̈́', ' ͊',
          ' ͋', ' ͌', ' ̃', ' ̂', ' ̌', ' ͐', ' ́', ' ̋', ' ̏', ' ̽', ' ̉', ' ͣ', ' ͤ', ' ͥ', ' ͦ', ' ͧ', ' ͨ', ' ͩ',
          ' ͪ', ' ͫ', ' ͬ', ' ͭ', ' ͮ', ' ͯ', ' ̾', ' ͛', ' ͆', ' ̚', ]
    dm = [' ̕', ' ̛', ' ̀', ' ́', ' ͘', ' ̡', ' ̢', ' ̧', ' ̨', ' ̴', ' ̵', ' ̶', ' ͜', ' ͝', ' ͞', ' ͟', ' ͠', ' ͢',
          ' ̸', ' ̷', ' ͡', ]
    letters = list(text)
    new_letters = []

    for letter in letters:
        a = letter

        if not a.isalpha():
            new_letters.append(a)
            continue

        num_accents = 0
        num_u = randint(num_accents_up[0], num_accents_up[1])
        num_d = randint(num_accents_down[0], num_accents_down[1])
        num_m = randint(num_accents_middle[0], num_accents_middle[1])
        while num_accents < max_accents_per_letter and num_u + num_m + num_d != 0:
            rand_int = randint(0, 2)
            if rand_int == 0:
                if num_u > 0:
                    a = a.strip() + du[randrange(0, len(du))].strip()
                    num_accents += 1
                    num_u -= 1
            elif rand_int == 1:
                if num_d > 0:
                    a = a.strip() + dd[randrange(0, len(dd))].strip()
                    num_d -= 1
                    num_accents += 1
            else:
                if num_m > 0:
                    a = a.strip() + dm[randrange(0, len(dm))].strip()
                    num_m -= 1
                    num_accents += 1

        new_letters.append(a)

    new_word = ''.join(new_letters)
    return new_word


def clear_emojis(target):
    """ Removes all Emojis from provided string """
    return get_emoji_regexp().sub(u'', target)
