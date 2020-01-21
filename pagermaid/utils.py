""" Libraries for python modules. """

from os import remove, popen
from emoji import get_emoji_regexp
from requests import head
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from wordcloud import WordCloud
from urllib import request, parse
from PIL import Image
from math import floor, ceil
from bs4 import BeautifulSoup
from random import random, randint, randrange, seed, choice
from time import sleep
from threading import Thread
from json import load as load_json
from re import sub, search, IGNORECASE
from pytz import country_names
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from pytz import timezone, country_timezones
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from pathlib import Path
from collections import deque
from youtube_dl import YoutubeDL
from pagermaid import config, path, redis


async def upload_result_image(context, result, target_file_path, reply_id):
    if not result:
        await context.edit("`Something wrong happened, please report this problem.`")
        try:
            remove("result.png")
            remove(target_file_path)
        except FileNotFoundError:
            pass
        raise ValueError
    try:
        await context.client.send_file(
            context.chat_id,
            "result.png",
            reply_to=reply_id
        )
    except ValueError:
        await context.edit("`An error occurred during the conversion.`")
        remove(target_file_path)
        raise ValueError
    await context.delete()
    remove(target_file_path)
    remove("result.png")


async def obtain_source_file(context):
    if context.fwd_from:
        return
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("Rendering image, please wait . . .")
    if reply:
        reply_id = reply.id
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    else:
        target_file_path = await context.download_media()
    if target_file_path is None:
        await context.edit("There are no attachment in target.")
        raise ValueError
    return reply_id, target_file_path


async def fetch_youtube_audio(context, url, reply_id):
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'outtmpl': "output.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    YoutubeDL(youtube_dl_options).download([url])
    try:
        await context.client.send_file(
            context.chat_id,
            "output.mp3",
            reply_to=reply_id
        )
    except ValueError:
        await context.edit("`An error occurred during the download.`")
        return
    await context.delete()
    remove("output.mp3")


async def make_top_cloud(context):
    await context.edit("Generating image . . .")
    command_list = []
    if not Path('/usr/bin/top').is_symlink():
        output = str(await execute("top -b -n 1")).split("\n")[7:]
    else:
        output = str(await execute("top -b -n 1")).split("\n")[4:]
    for line in output[:-1]:
        line = sub(r'\s+', ' ', line).strip()
        fields = line.split(" ")
        try:
            if fields[11].count("/") > 0:
                command = fields[11].split("/")[0]
            else:
                command = fields[11]

            cpu = float(fields[8].replace(",", "."))
            mem = float(fields[9].replace(",", "."))

            if command != "top":
                command_list.append((command, cpu, mem))
        except BaseException:
            pass
    command_dict = {}
    for command, cpu, mem in command_list:
        if command in command_dict:
            command_dict[command][0] += cpu
            command_dict[command][1] += mem
        else:
            command_dict[command] = [cpu + 1, mem + 1]

    resource_dict = {}

    for command, [cpu, mem] in command_dict.items():
        resource_dict[command] = (cpu ** 2 + mem ** 2) ** 0.5

    width, height = None, None
    try:
        width, height = ((popen("xrandr | grep '*'").read()).split()[0]).split("x")
        width = int(width)
        height = int(height)
    except BaseException:
        pass
    if not width or not height:
        width = int(config['width'])
        height = int(config['height'])
    background = config['background']
    margin = int(config['margin'])

    cloud = WordCloud(
        background_color=background,
        width=width - 2 * int(margin),
        height=height - 2 * int(margin)
    ).generate_from_frequencies(resource_dict)

    cloud.to_file("cloud.png")


async def upload_sticker(animated, bot, message, context, file, conversation):
    if animated:
        await bot.forward_messages(
            'Stickers', [message.id], context.chat_id)
    else:
        file.seek(0)
        await context.edit("Uploading image . . .")
        await conversation.send_file(file, force_document=True)


async def add_sticker(conversation, command, pack_title, pack_name, bot, animated, message, context, file, emoji):
    await conversation.send_message(command)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message(pack_title)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await upload_sticker(animated, bot, message, context, file, conversation)
    await conversation.get_response()
    await conversation.send_message(emoji)
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message("/publish")
    if animated:
        await conversation.get_response()
        await conversation.send_message(f"<{pack_title}>")
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message("/skip")
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message(pack_name)
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)


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


async def changelog_gen(repo, diff):
    result = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        result += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return result


async def branch_check(branch):
    official = ['master', 'staging']
    for k in official:
        if k == branch:
            return 1
    return


async def send_prune_notify(context, count):
    return await context.client.send_message(
        context.chat_id,
        "Deleted "
        + str(count)
        + " messages."
    )


async def attach_log(context, result):
    """ Method to attach logs for messages that are too long. """
    file = open("output.log", "w+")
    file.write(result)
    file.close()
    await context.client.send_file(
        context.chat_id,
        "output.log",
        reply_to=context.id,
    )
    remove("output.log")


async def get_timezone(target):
    """ Returns timezone of the parameter in command. """
    if "(Uk)" in target:
        target = target.replace("Uk", "UK")
    if "(Us)" in target:
        target = target.replace("Us", "US")
    if " Of " in target:
        target = target.replace(" Of ", " of ")
    if "(Western)" in target:
        target = target.replace("(Western)", "(western)")
    if "Minor Outlying Islands" in target:
        target = target.replace("Minor Outlying Islands", "minor outlying islands")
    if "Nl" in target:
        target = target.replace("Nl", "NL")

    for country_code in country_names:
        if target == country_names[country_code]:
            return timezone(country_timezones[country_code][0])
    try:
        if country_names[target]:
            return timezone(country_timezones[target][0])
    except KeyError:
        return


async def resize_image(photo):
    """ Photo resize to match sticker standards. """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


async def fetch_user(target):
    """ Fetch information of the target user. """
    if target.reply_to_msg_id:
        previous_message = await target.get_reply_message()
        replied_user = await target.client(GetFullUserRequest(previous_message.from_id))
    else:
        user = target.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            self_user = await target.client.get_me()
            user = self_user.id

        if target.message.entities is not None:
            probable_user_mention_entity = target.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await target.client(GetFullUserRequest(user_id))
                return replied_user
        try:
            user_object = await target.client.get_entity(user)
            replied_user = await target.client(GetFullUserRequest(user_object.id))
        except (TypeError, ValueError) as err:
            await target.edit(str(err))
            return None

    return replied_user


async def generate_strings(replied_user):
    """ Generates the needed strings for a user. """
    user_id = replied_user.user.id
    first_name = replied_user.user.first_name
    last_name = replied_user.user.last_name
    common_chat = replied_user.common_chats_count
    user_name = replied_user.user.username
    user_bio = replied_user.about
    is_bot = replied_user.user.bot
    restricted = replied_user.user.restricted
    verified = replied_user.user.verified
    first_name = first_name.replace("\u2060", "") if first_name else (
        "This user does not have a first name.")
    last_name = last_name.replace("\u2060", "") if last_name else (
        "This user does not have a last name.")
    user_name = "@{}".format(user_name) if user_name else (
        "This user does not have a username.")
    user_bio = "This user has no bio." if not user_bio else user_bio

    caption = "**Profile:** \n"
    caption += f"First Name: {first_name} \n"
    caption += f"Last Name: {last_name} \n"
    caption += f"Username: {user_name} \n"
    caption += f"Bot: {is_bot} \n"
    caption += f"Restricted: {restricted} \n"
    caption += f"Verified: {verified} \n"
    caption += f"ID: `{user_id}` \n"
    caption += f"Bio: `{user_bio}` \n"
    caption += f"Common Chats: {common_chat} \n"
    caption += f"Permanent Link: "
    caption += f"[{first_name} {last_name}](tg://user?id={user_id})" \
        if last_name != "This user does not have a " \
                        "last name." else f"[{first_name}](tg://user?id={user_id})"
    return caption


def last_replace(s, old, new):
    """ Helper util for owoifier. """
    li = s.rsplit(old, 1)
    return new.join(li)


def stutter(text):
    """Add a stutter"""
    words = text.split()
    first_letter = words[0][0]

    letter_stutter = f"{first_letter}-{first_letter.lower()}-{first_letter.lower()}"

    if len(words[0]) > 1:
        words[0] = letter_stutter + words[0][1:]
    else:
        words[0] = letter_stutter

    return " ".join(words)


def weebify(text):
    """Replace words and phrases"""
    with open(f"{path}/assets/replacements.json") as fp:
        replacements = load_json(fp)

    for expression in replacements:
        replacement = replacements[expression]
        text = sub(expression, replacement, text, flags=IGNORECASE)

    return text


def owoifier(text):
    """ Converts your text to OwO """
    smileys = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω´・)', '(´・ω・`)']

    text = weebify(text)
    text = stutter(text)
    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')
    text = last_replace(text, '!', '! {}'.format(choice(smileys)))
    text = last_replace(text, '?', '? owo')
    text = last_replace(text, '.', '. {}'.format(choice(smileys)))
    text = text + " desu"

    for v in ['a', 'o', 'u', 'A', 'O', 'U']:
        if 'n{}'.format(v) in text:
            text = text.replace('n{}'.format(v), 'ny{}'.format(v))
        if 'N{}'.format(v) in text:
            text = text.replace('N{}'.format(v), 'N{}{}'.format('Y' if v.isupper() else 'y', v))

    return text


def mocker(text, diversity_bias=0.5, random_seed=None):
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
                    a = combine_with_diacritic(a, du)
                    num_accents += 1
                    num_u -= 1
            elif rand_int == 1:
                if num_d > 0:
                    a = combine_with_diacritic(a, dd)
                    num_d -= 1
                    num_accents += 1
            else:
                if num_m > 0:
                    a = combine_with_diacritic(a, dm)
                    num_m -= 1
                    num_accents += 1

        new_letters.append(a)

    new_word = ''.join(new_letters)
    return new_word


def combine_with_diacritic(letter, diacritic_list):
    """ The fox. """
    return letter.strip() + diacritic_list[randrange(0, len(diacritic_list))].strip()


def strb(redis_string):
    """ Process strings for redis. """
    return str(redis_string)[2:-1]


def format_sed(data):
    """ Separate sed arguments. """
    try:
        if (
                len(data) >= 1 and
                data[1] in ("/", ":", "|", "_") and
                data.count(data[1]) >= 2
        ):
            target = data[1]
            start = counter = 2
            while counter < len(data):
                if data[counter] == "\\":
                    counter += 1

                elif data[counter] == target:
                    replace = data[start:counter]
                    counter += 1
                    start = counter
                    break

                counter += 1

            else:
                return None

            while counter < len(data):
                if (
                        data[counter] == "\\" and
                        counter + 1 < len(data) and
                        data[counter + 1] == target
                ):
                    data = data[:counter] + data[counter + 1:]

                elif data[counter] == target:
                    replace_with = data[start:counter]
                    counter += 1
                    break

                counter += 1
            else:
                return replace, data[start:], ""

            flags = ""
            if counter < len(data):
                flags = data[counter:]
            return replace, replace_with, flags.lower()
        return None
    except IndexError:
        pass


def redis_check():
    try:
        redis.ping()
        return True
    except BaseException:
        return False


def clear_emojis(target):
    """ Removes all Emojis from provided string """
    return get_emoji_regexp().sub(u'', target)


def url_tracer(url):
    """ Method to trace URL redirects. """
    while True:
        yield url
        try:
            response = head(url)
        except MissingSchema:
            break
        except InvalidURL:
            break
        except ConnectionError:
            break
        if 300 < response.status_code < 400:
            url = response.headers['location']
        else:
            break


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


class GoogleSearch:
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0"
    SEARCH_URL = "https://google.com/search"
    RESULT_SELECTOR = "div.r > a"
    TOTAL_SELECTOR = "#resultStats"
    RESULTS_PER_PAGE = 10
    DEFAULT_HEADERS = [
        ('User-Agent', USER_AGENT),
        ("Accept-Language", "en-US,en;q=0.5"),
    ]

    def search(self, query, num_results=10, prefetch_pages=True, prefetch_threads=10):
        search_results = []
        pages = int(ceil(num_results / float(GoogleSearch.RESULTS_PER_PAGE)))
        fetcher_threads = deque([])
        total = None
        for i in range(pages):
            start = i * GoogleSearch.RESULTS_PER_PAGE
            opener = request.build_opener()
            opener.addheaders = GoogleSearch.DEFAULT_HEADERS
            response = opener.open(GoogleSearch.SEARCH_URL + "?q=" + parse.quote(query) + ("" if start == 0 else (
                    "&start=" + str(start))))
            soup = BeautifulSoup(response.read(), "lxml")
            response.close()
            if total is None:
                total_text = soup.select(GoogleSearch.TOTAL_SELECTOR)[0].children.__next__()
                total = int(sub("[', ]", "", search("(([0-9]+[', ])*[0-9]+)", total_text).group(1)))
            results = self.parse_results(soup.select(GoogleSearch.RESULT_SELECTOR))
            if len(search_results) + len(results) > num_results:
                del results[num_results - len(search_results):]
            search_results += results
            if prefetch_pages:
                for result in results:
                    while True:
                        running = 0
                        for thread in fetcher_threads:
                            if thread.is_alive():
                                running += 1
                        if running < prefetch_threads:
                            break
                        sleep(1)
                    fetcher_thread = Thread(target=result.get_text)
                    fetcher_thread.start()
                    fetcher_threads.append(fetcher_thread)
        for thread in fetcher_threads:
            thread.join()
        return SearchResponse(search_results, total)

    @staticmethod
    def parse_results(results):
        search_results = []
        for result in results:
            url = result["href"]
            title = result.find_all('h3')[0].text
            text = result.parent.parent.find_all('div', {'class': 's'})[0].text
            search_results.append(SearchResult(title, url, text))
        return search_results


class SearchResponse:
    def __init__(self, results, total):
        self.results = results
        self.total = total


class SearchResult:
    def __init__(self, title, url, text):
        self.title = title
        self.url = url
        self.text = text

    def get_text(self):
        return self.text

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()
