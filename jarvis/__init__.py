""" Jarvis initialization. """

import os

from sys import version_info
from logging import basicConfig, getLogger, INFO, DEBUG
from distutils.util import strtobool as sb

from dotenv import load_dotenv
from requests import get
from telethon import TelegramClient
import redis

load_dotenv("config.env")

# logging stuff
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get("CONSOLE_LOGGER_VERBOSE", "False"))
if CONSOLE_LOGGER_VERBOSE:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=DEBUG,
    )
else:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=INFO
    )
LOGS = getLogger(__name__)

if version_info[0] < 3 or version_info[1] < 6:
    LOGS.error(
        "Please upgrade your python interpreter."
    )
    exit(1)

API_KEY = os.environ.get("API_KEY", None)
API_HASH = os.environ.get("API_HASH", None)
bot = TelegramClient("jarvis", API_KEY, API_HASH)

REDIS = redis.StrictRedis(host='localhost', port=6379, db=3)


def redis_check():
    try:
        REDIS.ping()
        return True
    except:
        return False


# a bunch of vars possibly used in other classes
COUNT_MSG = 0
USERS = {}
WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
WIDE_MAP[0x20] = 0x3000
COUNT_PM = {}
LASTMSG = {}
ENABLE_KILLME = True
CMD_HELP = {}
AFKREASON = "work"
