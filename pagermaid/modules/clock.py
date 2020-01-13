""" This module handles world clock related utility. """

from os import environ
from dotenv import load_dotenv
from datetime import datetime
from pytz import country_names
from pagermaid import command_help
from pagermaid.listener import listener, diagnostics
from pagermaid.utils import get_timezone

load_dotenv("config.env")
region = environ.get("APPLICATION_REGION", "United States")


@listener(outgoing=True, command="time")
@diagnostics
async def time(context):
    """ For querying time. """
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
