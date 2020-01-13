""" PagerMaid launch sequence. """

from importlib import import_module
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from pagermaid import logs, bot
from pagermaid.modules import all_modules

invalid_phone = '\nInvalid phone number entered.' \
                '\nPlease make sure you specified' \
                '\nyour country code in the string.'

try:
    bot.start()
except PhoneNumberInvalidError:
    print(invalid_phone)
    exit(1)

for module_name in all_modules:
    try:
        imported_module = import_module("pagermaid.modules." + module_name)
    except BaseException:
        logs.info(f"Unable to load module {module_name}.")

logs.info("PagerMaid have started, The prefix is -, type -help for help message.")

bot.run_until_disconnected()
