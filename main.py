import requests
import bs4
import discord
import asyncio
import math
from ast import literal_eval


client = discord.Client()


class SnowAlertSystem:
    @staticmethod
    def text_from_html(body):
        soup = bs4.BeautifulSoup(body, 'html.parser')
        text = soup.find(class_="cs-column-text emergency-alert-header").get_text()
        return text

    @staticmethod
    def get_warning():
        return SnowAlertSystem.text_from_html(requests.get("http://bsd405.org").text)

    @staticmethod
    async def check_bsd(last):
        await client.wait_until_ready()
        while not client.is_closed:
            if SnowAlertSystem.get_warning() != last and SnowAlertSystem.get_warning() != "":
                last = SnowAlertSystem.get_warning()
                await client.send_message(ANNOUNCEMENTS, "`{0}`".format(last.strip()))
            await asyncio.sleep(5)


class Response:
    def __init__(self, message):
        self.message = message
        self.text = message.content.lower()
        self.words = self.text.split(" ")
        self.do = (Response.triggers[set_phrase] for set_phrase in Response.triggers.keys()
                   if all(words in self.text for words in set_phrase))
        self.responses = [getattr(self, foo.__name__)() for foo in self.do]

    def snowman(self):
        if self.message.author.name in ban_list:
            return "{0} doesn't deserve ANY snowmen".format(self.message.author.name)
        else:
            print(self.message.author.name)
            print(ban_list)
            snow_word = "snowmen" if "snowmen" in self.text else "snowman"
            try:
                between = self.text[self.text.index("give me") + 7:self.text.index(snow_word)].strip()
                if str(between) == "a":
                    snowman_count = 1
                else:
                    snowman_count = round(eval(between))
            except:
                return
            if snowman_count > 0:
                return "☃" * min(snowman_count, 128)

    def kindred_spirit(self):
        return "A kindred spirit from {0}".format(self.message.author.name)

    def friend(self):
        return "I'm a friend"

    triggers = {
        ("give me", "snowman"): snowman,
        ("give me", "snowmen"): snowman,
        ("☃",): kindred_spirit,
        ("frosty is a friend",): friend
    }


@client.event
async def on_message(message):
    if not message.author.bot:
        for r in Response(message).responses:
            if r is not None:
                await client.send_message(message.channel, r)


with open("ban_list.txt", "r") as bl:
    ban_list = list(map(lambda x: x.rstrip(), bl.readlines()))
    

with open("data.txt", "r") as dat:
    lines = dat.read().splitlines()
    ANNOUNCEMENTS = discord.Object(id=lines[0])
    TOKEN = lines[1]

last_warning = SnowAlertSystem.get_warning()
client.loop.create_task(SnowAlertSystem.check_bsd(last_warning))
client.run(TOKEN)
