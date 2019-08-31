""" A jarvis class for event related stuff. """

import traceback

from telethon import events
from time import gmtime, strftime
from os import remove
from sys import exc_info
from telethon.events import StopPropagation
from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from jarvis import bot


def register(**args):
    """ Register a new event. """
    pattern = args.get('pattern', None)
    disable_edited = args.get('disable_edited', False)

    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern

    if "disable_edited" in args:
        del args['disable_edited']

    def decorator(func):
        if not disable_edited:
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
            # create = {
            #     'error': str(exc_info()[1]),
            #     'date': datetime.now()
            # }
            notification = "An error occurred while the server is interpreting this command." \
                           "If you want to help, forward the attached file and add contexts of" \
                           "the error to the [maintainer](tg://user?id=503691334)."
            report = "# Generated: " + time_string + ". \n" \
                     "# ChatID: " + str(context.chat_id) + ". \n" \
                     "# UserID: " + str(context.sender_id) + ". \n" \
                     "# Message: " + "\n-----BEGIN TARGET MESSAGE-----\n" \
                     "" + context.text + "\n-----END TARGET MESSAGE-----\n" \
                     "# Traceback: " + "\n-----BEGIN TRACEBACK-----\n" \
                     "" + str(traceback.format_exc()) + "\n-----END TRACEBACK-----\n" \
                     "# Error: \"" + str(exc_info()[1]) + "\". \n" \
                     "# Revision: " + revision_result + "."
            report_file = open("error_report.jarvis", "w+")
            report_file.write(report)
            report_file.close()

            await context.client.send_file(
                context.chat_id,
                "error_report.jarvis",
                caption=notification
            )
            remove("error_report.jarvis")
            return
    return handler
