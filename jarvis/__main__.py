""" Jarvis launch sequence. """

from importlib import import_module
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from jarvis import logs, bot
from jarvis.modules import all_modules

invalid_phone = '\nInvalid phone number entered.' \
                '\nPlease make sure you specified' \
                '\nyour country code in the string.'

try:
    bot.start()
except PhoneNumberInvalidError:
    print(invalid_phone)
    exit(1)

for module_name in all_modules:
    imported_module = import_module("jarvis.modules." + module_name)

logs.info("Jarvis have started, The prefix is -, type -help for help message.")

bot.run_until_disconnected()
