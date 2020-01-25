""" PagerMaid module that contains utilities related to system status. """

from os import remove, popen
from datetime import datetime
from speedtest import Speedtest
from telethon import functions
from platform import python_version, uname
from wordcloud import WordCloud
from telethon import version as telethon_version
from sys import platform
from re import sub
from pathlib import Path
from pagermaid import log, config, redis_status
from pagermaid.listener import listener
from pagermaid.utils import execute


@listener(outgoing=True, command="sysinfo",
          description="Retrieve system information via neofetch.")
async def sysinfo(context):
    """ Retrieve system information via neofetch. """
    result = await execute("neofetch --config none --stdout")
    await context.edit("`" + result + "`")


@listener(outgoing=True, command="fortune",
          description="Reads a fortune cookie message.")
async def fortune(context):
    """ Reads a fortune cookie. """
    result = await execute("fortune")
    if result == "/bin/sh: fortune: command not found":
        await context.edit("`No fortune cookies on this system.`")
        return
    await context.edit(result)


@listener(outgoing=True, command="fbcon",
          description="Takes screenshot of currently binded framebuffer console.")
async def tty(context):
    """ Screenshots a TTY and prints it. """
    await context.edit("Taking screenshot of framebuffer console . . .")
    message_id_to_reply = context.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    result = await execute("fbdump | magick - image.png")
    if result == "/bin/sh: fbdump: command not found":
        await context.edit("`fbdump does not exist on this system.`")
        remove("image.png")
        return
    if result == "/bin/sh: convert: command not found":
        await context.edit("`ImageMagick does not exist on this system.`")
        remove("image.png")
        return
    if result == "Failed to open /dev/fb0: Permission denied":
        await context.edit("`User not in video group.`")
        remove("image.png")
        return
    try:
        await context.client.send_file(
            context.chat_id,
            "image.png",
            caption="Screenshot of currently attached tty.",
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply
        )
        await log("Screenshot of binded framebuffer console taken.")
    except ValueError:
        await context.edit("File is not generated due to unexpected error.")
        return
    await context.delete()
    remove("image.png")


@listener(outgoing=True, command="status",
          description="Output the status of PagerMaid.")
async def status(context):
    hostname = uname().node
    kernel = uname().release
    database = "Redis is malfunctioning."
    if redis_status():
        database = "Connected to Redis."
    await context.edit(
        "`"
        "PagerMaid is online. \n\n"
        f"Hostname: {hostname} \n"
        f"Database Status: {database} \n"
        f"Host Platform: {platform} \n"
        f"Kernel Version: {kernel} \n"
        f"Python Version: {python_version()} \n"
        f"Library version: {telethon_version.__version__}"
        "`"
    )


@listener(outgoing=True, command="speedtest",
          description="Execute the speedtest script and outputs your internet speed.")
async def speedtest(context):
    """ Tests internet speed using speedtest. """
    await context.edit("Executing test scripts . . .")
    test = Speedtest()
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


@listener(outgoing=True, command="connection",
          description="Displays connection information between PagerMaid and Telegram.")
async def connection(context):
    """ Displays connection information between PagerMaid and Telegram. """
    datacenter = await context.client(functions.help.GetNearestDcRequest())
    await context.edit(
        f"Region `{datacenter.country}` \n"
        f"Connected Datacenter `{datacenter.this_dc}` \n"
        f"Nearest Datacenter `{datacenter.nearest_dc}`"
    )


@listener(outgoing=True, command="ping",
          description="Calculates latency between PagerMaid and Telegram.")
async def ping(context):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await context.edit("`Pong!`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await context.edit("`Pong!|%sms`" % duration)


@listener(outgoing=True, command="topcloud",
          description="Generates a word cloud of resource-hungry processes.")
async def topcloud(context):
    """ Generates a word cloud of resource-hungry processes. """
    if context.fwd_from:
        return
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
    await context.edit("Uploading image . . .")
    await context.client.send_file(
        context.chat_id,
        "cloud.png",
        reply_to=None,
        caption="Cloud of running processes."
    )
    remove("cloud.png")
    await context.delete()
    await log("Generated process word cloud.")


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
