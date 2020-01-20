""" This module contains utils to configure your account. """

from os import remove
from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import PhotoExtInvalidError, UsernameOccupiedError, AboutTooLongError, \
    FirstNameInvalidError, UsernameInvalidError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import DeletePhotosRequest, GetUserPhotosRequest, UploadProfilePhotoRequest
from telethon.tl.types import InputPhoto, MessageMediaPhoto
from pagermaid import bot, log
from pagermaid.listener import listener
from pagermaid.utils import generate_strings, fetch_user


@listener(outgoing=True, command="username",
          description="sets the username.",
          parameters="<username>")
async def username(context):
    """ Reconfigure your username. """
    result = context.pattern_match.group(1)
    try:
        await bot(UpdateUsernameRequest(result))
    except UsernameOccupiedError:
        await context.edit("Username is taken.")
        return
    except UsernameInvalidError:
        await context.edit("Invalid username.")
        return
    await context.edit("Username have been updated.")
    await log(f"Username has been set to {result}.")


@listener(outgoing=True, command="name",
          description="Alters the display name.",
          parameters="<first name> <last name>")
async def name(context):
    """ Updates your display name. """
    new_name = context.pattern_match.group(1)
    if " " not in new_name:
        first_name = new_name
        last_name = " "
    else:
        split = new_name.split(" ", 1)
        first_name = split[0]
        last_name = split[1]
    try:
        await bot(UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name))
    except FirstNameInvalidError:
        await context.edit("`Invalid first name.`")
        return
    await context.edit("`Display name is successfully altered.`")
    if last_name != " ":
        await log(f"Changed display name to `{first_name} {last_name}`.")
    else:
        await log(f"Changed display name to `{new_name}`.")


@listener(outgoing=True, command="pfp",
          description="Set attachment of message replied to as profile picture.")
async def pfp(context):
    """ Sets your profile picture. """
    reply = await context.get_reply_message()
    photo = None
    await context.edit("Setting profile picture . . .")
    if reply.media:
        if isinstance(reply.media, MessageMediaPhoto):
            photo = await bot.download_media(message=reply.photo)
        elif "image" in reply.media.document.mime_type.split('/'):
            photo = await bot.download_file(reply.media.document)
        else:
            await context.edit("Unable to parse attachment as image.")

    if photo:
        try:
            await bot(UploadProfilePhotoRequest(
                await bot.upload_file(photo)
            ))
            remove(photo)
            await context.edit("Profile picture has been updated.")
        except PhotoCropSizeSmallError:
            await context.edit("The image dimensions are smaller than minimum requirement.")
        except ImageProcessFailedError:
            await context.edit("An error occurred while the server is interpreting the command.")
        except PhotoExtInvalidError:
            await context.edit("Unable to parse attachment as image.")


@listener(outgoing=True, command="bio",
          description="Sets the biography to the string in the parameter.",
          parameters="<string>")
async def bio(context):
    """ Sets your bio. """
    result = context.pattern_match.group(1)
    try:
        await bot(UpdateProfileRequest(about=result))
    except AboutTooLongError:
        await context.edit("`Provided string is too long.`")
        return
    await context.edit("`Bio has been altered successfully.`")


@listener(outgoing=True, command="rmpfp",
          description="Deletes defined amount of profile pictures.",
          parameters="<integer>")
async def rmpfp(context):
    """ Removes your profile picture. """
    group = context.text[8:]
    if group == 'all':
        limit = 0
    elif group.isdigit():
        limit = int(group)
    else:
        limit = 1

    pfp_list = await bot(GetUserPhotosRequest(
        user_id=context.from_id,
        offset=0,
        max_id=0,
        limit=limit))
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


@listener(outgoing=True, command="profile",
          description="Shows user profile in a large message.",
          parameters="<username>")
async def profile(context):
    """ Queries profile of a user. """
    if context.fwd_from:
        return

    await context.edit("Generating user profile summary . . .")
    replied_user = await fetch_user(context)
    caption = await generate_strings(replied_user)
    reply_to = context.message.reply_to_msg_id
    photo = await context.client.download_profile_photo(
        replied_user.user.id,
        "./" + str(replied_user.user.id) + ".jpg",
        download_big=True
    )

    if not reply_to:
        reply_to = None

    try:
        await context.client.send_file(
            context.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=reply_to
        )

        if not photo.startswith("http"):
            remove(photo)
        await context.delete()
        return
    except TypeError:
        await context.edit(caption)

    remove(photo)
