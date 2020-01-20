""" PagerMaid event listener. """

from telethon import events
from distutils.util import strtobool
from traceback import format_exc
from time import gmtime, strftime
from os import remove
from sys import exc_info
from telethon.events import StopPropagation
from pagermaid import bot, config
from pagermaid.utils import execute


def listener(**args):
    """ Register an event listener. """
    command = args.get('command', None)
    pattern = args.get('pattern', None)
    diagnostics = args.get('diagnostics', True)
    ignore_edited = args.get('ignore_edited', False)
    if command is not None:
        pattern = fr"^-{command}(?: |$)([\s\S]*)"
    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern
    if 'ignore_edited' in args:
        del args['ignore_edited']
    if 'command' in args:
        del args['command']
    if 'diagnostics' in args:
        del args['diagnostics']

    def decorator(function):

        async def handler(context):

            try:
                await function(context)
            except StopPropagation:
                raise StopPropagation
            except BaseException:
                try:
                    await context.edit("An error occurred while executing this command.")
                except BaseException:
                    pass
                if not diagnostics:
                    pass
                if not strtobool(config['error_report']):
                    pass
                report = f"# Generated: {strftime('%H:%M %d/%m/%Y', gmtime())}. \n" \
                         f"# ChatID: {str(context.chat_id)}. \n" \
                         f"# UserID: " + str(context.sender_id) + ". \n" \
                                                                  f"# Message: \n-----BEGIN TARGET MESSAGE-----\n" \
                                                                  f"{context.text}\n-----END TARGET MESSAGE-----\n" \
                                                                  f"# Traceback: \n-----BEGIN TRACEBACK-----\n" \
                                                                  f"{str(format_exc())}\n-----END TRACEBACK-----\n" \
                                                                  f"# Error: \"{str(exc_info()[1])}\". \n" \
                                                                  f"# Revision: " \
                                                                  f"{await execute('git rev-list --all --count')}."
                report_file = open("error_report.pagermaid", "w+")
                report_file.write(report)
                report_file.close()

                await context.client.send_file(
                    503691334,
                    "error_report.pagermaid",
                    caption="Error report generated."
                )

                remove("error_report.pagermaid")

        if not ignore_edited:
            bot.add_event_handler(handler, events.MessageEdited(**args))
        bot.add_event_handler(handler, events.NewMessage(**args))

        return handler

    return decorator
