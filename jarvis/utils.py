""" Libraries for python modules. """

from os import remove
from requests import head
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from PIL import Image
from math import floor
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName


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


async def resize_photo(photo):
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


async def generate_strings(replied_user, event):
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
    photo = await event.client.download_profile_photo(
        user_id,
        "./" + str(user_id) + ".jpg",
        download_big=True
    )
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
    caption += f"ID: `{user_id}` \n \n"
    caption += f"Bio: `{user_bio}` \n \n"
    caption += f"Common Chats: {common_chat} \n"
    caption += f"Permanent Link: "
    caption += f"[{first_name} {last_name}](tg://user?id={user_id})" \
        if last_name is not "This user does not have a " \
                            "last name." else f"[{first_name}](tg://user?id={user_id})"
    return photo, caption


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
