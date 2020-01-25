""" This module handles world clock related utility. """

from datetime import datetime
from pytz import country_names, country_timezones, timezone
from pagermaid import config
from pagermaid.listener import listener


@listener(outgoing=True, command="time",
          description="Displays time of specific region, defaults to configured value if parameter is empty.",
          parameters="<region>")
async def time(context):
    """ For querying time. """
    country = context.pattern_match.group(1).title()
    time_form = "%I:%M %p"
    date_form = "%A %d/%m/%y"
    if not country:
        time_zone = await get_timezone(config['application_region'])
        await context.edit(
            f"**Time in {config['application_region']}**\n"
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
