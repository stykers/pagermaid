""" Jarvis launch sequence. """

from importlib import import_module
from sqlite3 import connect
from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from jarvis import logs, bot, database_test
from jarvis.modules import all_modules

db = connect("database.db")
cursor = db.cursor()
cursor.execute("SELECT * FROM ChatStorage")
all_rows = cursor.fetchall()
invalid_phone = '\nInvalid phone number entered.' \
                '\nPlease make sure you specified' \
                '\nyour country code in the string.'

for i in all_rows:
    database_test.append(i[0])
connect("database.db").close()
try:
    bot.start()
except PhoneNumberInvalidError:
    print(invalid_phone)
    exit(1)

for module_name in all_modules:
    imported_module = import_module("jarvis.modules." + module_name)

logs.info("Jarvis has started, The prefix is s!, type s!help for help message.")

if len(argv) not in (1, 3, 4):
    bot.disconnect()
else:
    bot.run_until_disconnected()
