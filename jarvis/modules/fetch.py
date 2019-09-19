""" Jarvis module for content modules. """

from youtube_dl import YoutubeDL
from pytube import YouTube
from pytube.helpers import safe_filename
from requests import get
from os import remove
from jarvis import bot, command_help, log, log_chatid
from jarvis.events import register, diagnostics
from jarvis.utils import execute


@register(outgoing=True, pattern=r"^-youtube (\S*) ?(\S*)")
@diagnostics
async def youtube(context):
    """ Downloads videos from youtube. """
    url = context.pattern_match.group(1)
    quality = context.pattern_match.group(2)

    await context.edit("`Requesting information . . .`")

    video = YouTube(url)

    if quality:
        video_stream = video.streams.filter(progressive=True,
                                            subtype="mp4",
                                            res=quality).first()
    else:
        video_stream = video.streams.filter(progressive=True,
                                            subtype="mp4").first()

    if video_stream is None:
        all_streams = video.streams.filter(progressive=True,
                                           subtype="mp4").all()
        available_qualities = ""

        for item in all_streams[:-1]:
            available_qualities += f"{item.resolution}, "
        available_qualities += all_streams[-1].resolution

        await context.edit("`The specified quality is invalid.\n"
                           "Select from the list below:\n**"
                           f"{available_qualities}`")
        return

    video_size = video_stream.filesize / 1000000

    if video_size >= 50:
        await context.edit(
            f"File too large, generating direct [link]({video_stream.url})."
        )
        return

    await context.edit("Receiving data from YouTube . . .")

    video_stream.download(filename=video.title)

    url = f"https://img.youtube.com/vi/{video.video_id}/maxresdefault.jpg"
    resp = get(url)
    with open('thumbnail.jpg', 'wb') as file:
        file.write(resp.content)

    await context.edit("Pushing to telegram . . .")
    await bot.send_file(context.chat_id,
                        f'{safe_filename(video.title)}.mp4',
                        caption=f"{video.title}",
                        thumb="thumbnail.jpg")

    remove(f"{safe_filename(video.title)}.mp4")
    remove('thumbnail.jpg')
    await context.delete()
    if log:
        await context.client.send_message(
            log_chatid, f"Downloaded {url} from YouTube."
        )
command_help.update({
    "youtube": "Parameter: -youtube <url>\
    \nUsage: Downloads a video from YouTube."
})
