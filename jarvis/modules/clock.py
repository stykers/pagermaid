""" This module handles world clock related utility. """

from os import environ
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
from pytz import country_names
from pytz import country_timezones
from jarvis import command_help
from jarvis.events import register

load_dotenv("config.env")
region = environ.get("APPLICATION_REGION", "United States")


@register(outgoing=True, pattern="^-time(?: |$)(.*)")
async def time(context):
    """ For querying time. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        country = context.pattern_match.group(1).title()
        time_form = "%I:%M %p"
        date_form = "%A %d/%m/%y"
        if not country:
            time_zone = await get_timezone(region)
            await context.edit(
                f"**Time in {region}**\n"
                f"`{datetime.now(time_zone).strftime(date_form)} "
                f"{datetime.now(time_zone).strftime(time_form)}`"
            )
            return

        time_zone = await get_timezone(country)
        if not time_zone:
            await context.edit("`Invalid parameter.`")
            return

        try:
            country_name = country_names[country]
        except KeyError:
            country_name = country

        await context.edit(f"**Time in {country_name}**\n"
                           f"`{datetime.now(time_zone).strftime(date_form)} "
                           f"{datetime.now(time_zone).strftime(time_form)}`")
command_help.update({
    "time": "Parameter: -time <region>\
    \nUsage: Displays time of specific region, reads from config file if parameter is empty."
})


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
