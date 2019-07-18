""" This module contains utils to configure your account. """

import os

from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import PhotoExtInvalidError, UsernameOccupiedError, AboutTooLongError,\
    FirstNameInvalidError, UsernameInvalidError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.tl.functions.photos import DeletePhotosRequest, GetUserPhotosRequest, UploadProfilePhotoRequest
from telethon.tl.types import InputPhoto, MessageMediaPhoto
from jarvis import command_help, bot
from jarvis.events import register


@register(outgoing=True, pattern="^-username (.*)")
async def username(context):
    """ Reconfigure your username. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        result = context.pattern_match.group(1)
        try:
            await bot(UpdateUsernameRequest(result))
        except UsernameOccupiedError:
            await context.edit("`Username is taken.`")
            return
        except UsernameInvalidError:
            await context.edit("`Invalid username.`")
            return
        await context.edit("`Username have been updated.`")


@register(outgoing=True, pattern="^-name")
async def name(context):
    """ Updates your display name. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        new = context.text[6:]
        if " " not in new:
            first = new
            last = ""
        else:
            split = new.split(" ", 1)
            first = split[0]
            last = split[1]
        try:
            await bot(UpdateProfileRequest(
                first_name=first,
                last_name=last))
        except FirstNameInvalidError:
            await context.edit("`Invalid first name.`")
            return
        await context.edit("`Display name is successfully altered.`")


@register(outgoing=True, pattern="^-pfp$")
async def pfp(context):
    """ Sets your profile picture. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        reply = await context.get_reply_message()
        photo = None
        if reply.media:
            if isinstance(reply.media, MessageMediaPhoto):
                photo = await bot.download_media(message=reply.photo)
            elif "image" in reply.media.document.mime_type.split('/'):
                photo = await bot.download_file(reply.media.document)
            else:
                await context.edit("`Unable to parse attachment as image.`")

        if photo:
            try:
                await bot(UploadProfilePhotoRequest(
                    await bot.upload_file(photo)
                ))
                os.remove(photo)
                await context.edit("`Profile picture has been updated.`")
            except PhotoCropSizeSmallError:
                await context.edit("`The image dimensions are smaller than minimum requirement.`")
            except ImageProcessFailedError:
                await context.edit("`An error occurred while the server is interpreting the command.`")
            except PhotoExtInvalidError:
                await context.edit("`Unable to parse attachment as image.`")


@register(outgoing=True, pattern="^-bio (.*)")
async def bio(context):
    """ Sets your bio. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        result = context.pattern_match.group(1)
        try:
            await bot(UpdateProfileRequest(about=result))
        except AboutTooLongError:
            await context.edit("`Provided string is too long.`")
            return
        await context.edit("`Bio has been altered successfully.`")


@register(outgoing=True, pattern=r"^-rm_pfp")
async def rm_pfp(context):
    """ Removes your profile picture. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        group = context.text[8:]
        if group == 'all':
            lim = 0
        elif group.isdigit():
            lim = int(group)
        else:
            lim = 1

        pfp_list = await bot(GetUserPhotosRequest(
            user_id=context.from_id,
            offset=0,
            max_id=0,
            limit=lim))
        input_photos = []
        for sep in pfp_list.photos:
            input_photos.append(
                InputPhoto(
                    id=sep.id,
                    access_hash=sep.access_hash,
                    file_reference=sep.file_reference
                )
            )
        await bot(DeletePhotosRequest(id=input_photos))
        await context.edit(f"`Removed {len(input_photos)} profile picture(s).`")


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


@register(pattern="-profile(?: |$)(.*)", outgoing=True)
async def profile(context):
    """ Queries profile of a user. """
    if context.fwd_from:
        return

    if not os.path.isdir("./"):
        os.makedirs("./")

    replied_user = await fetch_user(context)

    photo, caption = await generate_strings(replied_user, context)

    message_id_to_reply = context.message.reply_to_msg_id

    if not message_id_to_reply:
        message_id_to_reply = None

    try:
        await context.client.send_file(
            context.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply,
            parse_mode="html"
        )

        if not photo.startswith("http"):
            os.remove(photo)
        await context.delete()

    except TypeError:
        await context.edit(caption, parse_mode="html")


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

    caption = "<b>Profile:</b> \n"
    caption += f"First Name: {first_name} \n"
    caption += f"Last Name: {last_name} \n"
    caption += f"Username: {user_name} \n"
    caption += f"Bot: {is_bot} \n"
    caption += f"Restricted: {restricted} \n"
    caption += f"Verified: {verified} \n"
    caption += f"ID: <code>{user_id}</code> \n \n"
    caption += f"Bio: \n<code>{user_bio}</code> \n \n"
    caption += f"Common Chats: {common_chat} \n"
    caption += f"Permanent Link: "
    caption += f"<a href=\"tg://user?id={user_id}\">{first_name}</a>"

    return photo, caption


command_help.update({
    "username": "Parameter: -username <text>\
    \nUsage: Sets the username."
})
command_help.update({
    "name": "Parameter: -name <text> <text>\
    \nUsage: Alters the display name."
})
command_help.update({
    "pfp": "Usage: -pfp\
    \nUsage: Sets profile picture to image replied to."
})
command_help.update({
    "bio": "-bio <text>\
    \nUsage: Sets the bio string."
})
command_help.update({
    "rm_pfp": "Parameter: -rm_pfp <amount>\
    \nUsage: Deletes part or all of your profile picture history."
})
