""" PagerMaid features that uses external HTTP APIs other than Telegram. """

from googletrans import Translator, LANGUAGES
from os import remove
from urllib import request, parse
from math import ceil
from time import sleep
from threading import Thread
from bs4 import BeautifulSoup
from gtts import gTTS
from re import compile as regex_compile
from re import search, sub
from collections import deque
from pagermaid import log
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, attach_log, fetch_youtube_audio


@listener(outgoing=True, command="translate",
          description="Translate the target message into specified language via Google Translate.",
          parameters="<language>")
async def translate(context):
    """ PagerMaid universal translator. """
    translator = Translator()
    text = await context.get_reply_message()
    message = context.pattern_match.group(1)
    lang = config['application_language']
    if message:
        pass
    elif text:
        message = text.text
    else:
        await context.edit("Invalid parameter.")
        return

    try:
        await context.edit("Generating translation . . .")
        result = translator.translate(clear_emojis(message), dest=lang)
    except ValueError:
        await context.edit("Language not found, please correct the error in the config file.")
        return

    source_lang = LANGUAGES[f'{result.src.lower()}']
    trans_lang = LANGUAGES[f'{result.dest.lower()}']
    result = f"**Translated** from {source_lang.title()}:\n{result.text}"

    if len(result) > 4096:
        await context.edit("Output exceeded limit, attaching file.")
        await attach_log(result, context.chat_id, "translation.txt", context.id)
        return
    await context.edit(result)
    if len(result) <= 4096:
        await log(f"Translated `{message}` from {source_lang} to {trans_lang}.")
    else:
        await log(f"Translated message from {source_lang} to {trans_lang}.")


@listener(outgoing=True, command="tts",
          description="Generates a voice message based on a string via Google Text to Speech.",
          parameters="<string>")
async def tts(context):
    """ Send TTS stuff as voice message. """
    text = await context.get_reply_message()
    message = context.pattern_match.group(1)
    lang = config['application_language']
    if message:
        pass
    elif text:
        message = text.text
    else:
        await context.edit("Invalid argument.")
        return

    try:
        await context.edit("Generating vocals . . .")
        gTTS(message, lang)
    except AssertionError:
        await context.edit("Invalid argument.")
        return
    except ValueError:
        await context.edit('Language not found, please correct the error in the config file.')
        return
    except RuntimeError:
        await context.edit('Error loading array of languages.')
        return
    google_tts = gTTS(message, lang)
    google_tts.save("vocals.mp3")
    with open("vocals.mp3", "rb") as audio:
        line_list = list(audio)
        line_count = len(line_list)
    if line_count == 1:
        google_tts = gTTS(message, lang)
        google_tts.save("vocals.mp3")
    with open("vocals.mp3", "r"):
        await context.client.send_file(context.chat_id, "vocals.mp3", voice_note=True)
        remove("vocals.mp3")
        if len(message) <= 4096:
            await log(f"Generated text to speech audio for `{message}`.")
        else:
            await log("Generated text to speech audio for message.")
        await context.delete()


@listener(outgoing=True, command="google",
          description="Searches Google for a specific query.",
          parameters="<query>")
async def google(context):
    """ Searches Google for a string. """
    query = context.pattern_match.group(1)
    await context.edit("Pulling results . . .")
    search_results = GoogleSearch().search(query=query)
    results = ""
    count = 0
    for result in search_results.results:
        if count == int(config['result_length']):
            break
        count += 1
        title = result.title
        link = result.url
        desc = result.text
        results += f"\n[{title}]({link}) \n`{desc}`\n"
    await context.edit(f"**Google** |`{query}`| 🎙 🔍 \n"
                       f"{results}",
                       link_preview=False)
    await log(f"Queried {query} on the Google search engine.")


@listener(outgoing=True, command="fetchaudio",
          description="Fetches audio file from multiple platforms.",
          parameters="<url>")
async def fetchaudio(context):
    """ Fetches audio from provided URL. """
    url = context.pattern_match.group(1)
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("Fetching audio . . .")
    if reply:
        reply_id = reply.id
    if url is None:
        await context.edit("Invalid arguments.")
        return
    youtube_pattern = regex_compile(r"^(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+")
    if youtube_pattern.match(url):
        if not await fetch_youtube_audio(url, context.chat_id, reply_id):
            await context.edit("The soundtrack failed to download.")
        await log(f"Fetched audio from {url}.")


class GoogleSearch:
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0"
    SEARCH_URL = "https://google.com/search"
    RESULT_SELECTOR = "div.r > a"
    TOTAL_SELECTOR = "#resultStats"
    RESULTS_PER_PAGE = 10
    DEFAULT_HEADERS = [
        ('User-Agent', USER_AGENT),
        ("Accept-Language", "en-US,en;q=0.5"),
    ]

    def search(self, query, num_results=10, prefetch_pages=True, prefetch_threads=10):
        search_results = []
        pages = int(ceil(num_results / float(GoogleSearch.RESULTS_PER_PAGE)))
        fetcher_threads = deque([])
        total = None
        for i in range(pages):
            start = i * GoogleSearch.RESULTS_PER_PAGE
            opener = request.build_opener()
            opener.addheaders = GoogleSearch.DEFAULT_HEADERS
            response = opener.open(GoogleSearch.SEARCH_URL + "?q=" + parse.quote(query) + ("" if start == 0 else (
                    "&start=" + str(start))))
            soup = BeautifulSoup(response.read(), "lxml")
            response.close()
            if total is None:
                total_text = soup.select(GoogleSearch.TOTAL_SELECTOR)[0].children.__next__()
                total = int(sub("[', ]", "", search("(([0-9]+[', ])*[0-9]+)", total_text).group(1)))
            results = self.parse_results(soup.select(GoogleSearch.RESULT_SELECTOR))
            if len(search_results) + len(results) > num_results:
                del results[num_results - len(search_results):]
            search_results += results
            if prefetch_pages:
                for result in results:
                    while True:
                        running = 0
                        for thread in fetcher_threads:
                            if thread.is_alive():
                                running += 1
                        if running < prefetch_threads:
                            break
                        sleep(1)
                    fetcher_thread = Thread(target=result.get_text)
                    fetcher_thread.start()
                    fetcher_threads.append(fetcher_thread)
        for thread in fetcher_threads:
            thread.join()
        return SearchResponse(search_results, total)

    @staticmethod
    def parse_results(results):
        search_results = []
        for result in results:
            url = result["href"]
            title = result.find_all('h3')[0].text
            text = result.parent.parent.find_all('div', {'class': 's'})[0].text
            search_results.append(SearchResult(title, url, text))
        return search_results


class SearchResponse:
    def __init__(self, results, total):
        self.results = results
        self.total = total


class SearchResult:
    def __init__(self, title, url, text):
        self.title = title
        self.url = url
        self.text = text

    def get_text(self):
        return self.text

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()
