""" Jarvis launch sequence. """

from importlib import import_module
from sqlite3 import connect
from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from jarvis import logs, bot, database_test
from jarvis.modules import all_modules

db = connect("database.db")
