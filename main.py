import requests
import bs4
import discord
import asyncio
import math
from ast import literal_eval


client = discord.Client()


def text_from_html(body):
    soup = bs4.BeautifulSoup(body, 'html.parser')
    text = soup.find(class_="cs-column-text emergency-alert-header").get_text()
    return text


def get_warning():
    return text_from_html(requests.get("http://bsd405.org").text)


async def check_bsd():
    global LAST
    await client.wait_until_ready()
    while not client.is_closed:
        if get_warning() != LAST and get_warning() != "":
            LAST = get_warning()
            await client.send_message(CHANNEL, "New warning: `{0}`".format(LAST.strip()))
        await asyncio.sleep(5)


@client.event
async def on_message(message):
    text = message.content.lower()
    if "give me" in text and ("snowmen" in text or "snowman" in text):
        snow_word = "snowmen" if "snowmen" in text else "snowman"
        try:
            between = text[text.index("give me")+7:text.index(snow_word)].strip()
            if str(between) == "a":
                snowman_count = 1
            else:
                snowman_count = int(literal_eval(between))
        except:
            return
        if message.author.name in ban_list:
            await client.send_message(message.channel, "{0} doesn't deserve ANY snowmen".format(message.author.name))
        else:
            if snowman_count > 0:
                await client.send_message(message.channel, "☃" * min(snowman_count, 128))


ban_list = ["nog642"]
LAST = get_warning()
CHANNEL = discord.Object(id='')
TOKEN = ''
client.loop.create_task(check_bsd())
client.run(TOKEN)
