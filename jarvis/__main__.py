""" Jarvis launch sequence. """

from importlib import import_module
from sqlite3 import connect
from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from jarvis import LOGS, bot
