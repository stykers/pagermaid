""" PagerMaid event listener. """

from telethon import events
from distutils.util import strtobool
from traceback import format_exc
from time import gmtime, strftime
from os import remove
from sys import exc_info
from telethon.events import StopPropagation
from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from pagermaid import bot, config


def listener(**args):
    """ Register a new event. """
    command = args.get('command', None)
    pattern = args.get('pattern', None)
    if command is not None:
        pattern = fr"^-{command}(?: |$)([\s\S]*)"
    ignore_edited = args.get('ignore_edited', False)

    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern

    if "ignore_edited" in args:
        del args['ignore_edited']

    if "command" in args:
        del args['command']

    def decorator(func):
        if not ignore_edited:
            bot.add_event_handler(func, events.MessageEdited(**args))
        bot.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def diagnostics(function):
    async def handler(context):
        try:
            await function(context)
        except StopPropagation:
            pass
        except BaseException:
            try:
                await context.edit("An error occurred while executing this command.")
            except BaseException:
                pass
            if not strtobool(config['error_report']):
                return
            time_string = strftime("%H:%M %d/%m/%Y", gmtime())
            command = "git rev-list --all --count"
            rev = await async_run(
                command,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout, stderr = await rev.communicate()
            revision_result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())
            report = "# Generated: " + time_string + ". \n" \
                     "# ChatID: " + str(context.chat_id) + ". \n" \
                     "# UserID: " + str(context.sender_id) + ". \n" \
                     "# Message: " + "\n-----BEGIN TARGET MESSAGE-----\n" \
                     "" + context.text + "\n-----END TARGET MESSAGE-----\n" \
                     "# Traceback: " + "\n-----BEGIN TRACEBACK-----\n" \
                     "" + str(format_exc()) + "\n-----END TRACEBACK-----\n" \
                     "# Error: \"" + str(exc_info()[1]) + "\". \n" \
                     "# Revision: " + revision_result + "."
            report_file = open("error_report.pagermaid", "w+")
            report_file.write(report)
            report_file.close()

            await context.client.send_file(
                503691334,
                "error_report.pagermaid",
                caption="Error report generated."
            )
            remove("error_report.pagermaid")
            return
    return handler
