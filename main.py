import requests
import bs4
import discord
import asyncio
import base64
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
        self.text = message.content
        self.lower_text = self.text.lower()
        self.words = self.text.split(" ")
        self.lower_words = self.lower_text.split(" ")
        self.author = self.message.author.name
        self.do = (Response.triggers[set_phrase] for set_phrase in Response.triggers.keys()
                   if all(words in self.lower_text for words in set_phrase))
        self.responses = [getattr(self, foo.__name__)() for foo in self.do]

    def snowman(self):
        if self.author in ban_list:
            return "{0} doesn't deserve ANY snowmen".format(self.message.author.name)
        else:
            snow_word = "snowmen" if "snowmen" in self.lower_text else "snowman"
            try:
                between = self.text[self.text.index("give me") + 7:self.text.index(snow_word)].strip()
                while True:
                    if between.startswith("'") and between.endswith("'"):
                        between = between[1:-1]
                    else:
                        break
                if str(between) == "a":
                    snowman_count = 1
                else:
                    if self.author in eval_list:
                        snowman_count = round(eval(between))
                    else:
                        snowman_count = round(literal_eval(between))
            except:
                return
            if snowman_count > 0:
                return "☃" * min(snowman_count, 128)

    def kindred_spirit(self):
        return "A kindred spirit from {0}".format(self.message.author.name)

    def friend(self):
        return "I'm a friend"

    def ban(self):
        try:
            i = self.lower_words.index("ban") + 1
            name = self.words[i]
            if name in ban_list:
                ban_list.remove(name)
                return "{0} has been removed from the ban list".format(name)
            else:
                ban_list.append(name)
                return "{0} has been banned".format(name)
        except:
            return

    def give_eval(self):
        if self.author == "Timothy Z.":
            try:
                i = self.lower_words.index("eval") + 1
                name = self.words[i]
                if name in eval_list:
                    eval_list.remove(name)
                    return "{0} has had their eval privileges revoked".format(name)
                else:
                    eval_list.append(name)
                    return "{0} now has eval privileges".format(name)
            except:
                return

    def where_money(self):
        return "CMU where {0}'s money at".format(self.author)

    triggers = {
        ("give me", "snowman"): snowman,
        ("give me", "snowmen"): snowman,
        ("☃",): kindred_spirit,
        ("frosty is a friend",): friend,
        ("ban ",): ban,
        ("give eval",): give_eval,
        ("cmu",): where_money
    }


@client.event
async def on_message(message):
    if not message.author.bot:
        for r in Response(message).responses:
            if r is not None:
                await client.send_message(message.channel, r)


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


eval_list = ["Timothy Z."]
ban_list = []
last_warning = SnowAlertSystem.get_warning()
client.loop.create_task(SnowAlertSystem.check_bsd(last_warning))


with open("data.txt", "r") as dat:
    lines = dat.read().splitlines()
    ANNOUNCEMENTS = discord.Object(id=lines[0])
    client.run(decode(input("Enter key: "), lines[1]))
