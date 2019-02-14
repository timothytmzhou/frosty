import requests
import bs4
import discord
import asyncio
import math
import numpy as np
from ast import literal_eval

client = discord.Client()


class SnowAlertSystem:
    ANNOUNCEMENTS = discord.Object(id=500749047364321344)

    def __init__(self):
        last_warning = SnowAlertSystem.get_warning()
        client.loop.create_task(SnowAlertSystem.check_bsd(last_warning))

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
                await client.send_message(SnowAlertSystem.ANNOUNCEMENTS, "`{0}`".format(last.strip()))
            await asyncio.sleep(5)


class Response:
    admin_list = []
    ban_list = []
    max_response_length = 128
    replies = {
        ("☃",): "A kindred spirit from {0}",
        ("frosty is a friend",): "I'm a friend"
    }

    def __init__(self, message):
        # Get data from message
        self.message = message
        self.text = message.content
        self.lower_text = self.text.lower()
        self.words = self.text.split(" ")
        self.lower_words = self.lower_text.split(" ")
        self.author = self.message.author.name

        # Execute all functions with matching trigger phrases
        self.do = (Response.triggers[set_phrase] for set_phrase in Response.triggers
                   if all(word in self.lower_text for word in set_phrase))
        self.say = [self.reply(keywords) for keywords in Response.replies
                    if all(word in self.lower_text for word in keywords)]
        self.responses = [foo(self) for foo in self.do] + self.say

    def reply(self, keyword):
        a = Response.replies[keyword]
        return a.format(self.author) if "{0}" in a else a

    def new_command(self):
        if self.author in Response.admin_list or self.author == "Timothy Z.":
            try:
                begin = self.lower_words.index("command") + 1
                sep = self.lower_words.index(":")
                trigger = tuple(self.lower_words[begin:sep])
                reply = ' '.join(self.words[sep+1:])
                Response.replies[trigger] = reply
                return "New command added: when someone says {0} I'll say {1}".format(', '.join(trigger), reply)
            except:
                return "New command failed. Check the syntax of your response."

    def remove_command(self):
        if self.author in Response.admin_list or self.author == "Timothy Z.":
            try:
                remove = self.words[self.words.index("command")+1]
                return "Trigger {0} with response {1} removed".format(remove, Response.replies[(remove,)].pop())
            except:
                return "Removing command failed. Check the syntax of your response."

    def ban(self):
        if self.author in Response.admin_list or self.author == "Timothy Z.":
            try:
                i = self.lower_words.index("ban") + 1
                name = self.words[i]
                if name in Response.ban_list:
                    Response.ban_list.remove(name)
                    return "{0} has been removed from the ban list".format(name)
                else:
                    if name in Response.admin_list:
                        Response.admin_list.remove(name)
                    Response.ban_list.append(name)
                    return "{0} has been banned".format(name)
            except:
                return "Ban failed. Check the syntax of your response"

    def give_admin(self):
        if self.author in Response.admin_list or self.author == "Timothy Z.":
            try:
                i = self.lower_words.index("admin") + 1
                name = self.words[i]
                if name in Response.admin_list:
                    Response.admin_list.remove(name)
                    return "{0} has had their admin privileges revoked".format(name)
                else:
                    Response.admin_list.append(name)
                    return "{0} now has admin privileges".format(name)
            except:
                return

    def snowman(self):
        if self.author in Response.ban_list:
            return "{0} doesn't deserve ANY snowmen".format(self.message.author.name)
        else:
            snow_word = "snowmen" if "snowmen" in self.lower_text else "snowman"
            start = self.lower_words.index("me") + 1
            end = self.lower_words.index(snow_word)
            try:
                between = ' '.join(self.words[start:end]).strip()
                while True:
                    if between.startswith("`") and between.endswith("`"):
                        between = between[1:-1]
                    else:
                        break
                if str(between) == "a":
                    snowman_count = 1
                else:
                    if self.author in Response.admin_list or self.author == "Timothy Z.":
                            snowman_count = int(eval(between))
                    else:
                        snowman_count = int(literal_eval(between))
            except:
                return
            if snowman_count > 0:
                return "☃" * min(snowman_count, Response.max_response_length)

    def frosty_say(self):
        if self.author in Response.admin_list or self.author == "Timothy Z.":
            try:
                return "DELETE//" + self.text.replace("frosty say", "")
            except:
                return "Frosty say failed. Check the syntax of your response"

    def command_list(self):
        message = "**Triggers:**\n"
        for t in Response.triggers:
            message += "When someone says `{0}` I'll execute {1}.\n".format(", ".join(t), Response.triggers[t].__name__)
        message += "**Replies:**\n"
        for r in Response.replies:
            message += "When someone says `{0}` I'll say back {1}.\n".format(", ".join(r), Response.replies[r])
        return message

    triggers = {
        ("give me", "snowman"): snowman,
        ("give me", "snowmen"): snowman,
        ("ban",): ban,
        ("frosty admin",): give_admin,
        ("frosty say",): frosty_say,
        ("add command",): new_command,
        ("remove command",): remove_command,
        ("command list",): command_list
    }


@client.event
async def on_message(message):
    if not message.author.bot:
        for r in Response(message).responses:
            if r is not None:
                if r.startswith("DELETE//"):
                    await client.delete_message(message)
                await client.send_message(message.channel, r.replace("DELETE//", ""))


snow_alert = SnowAlertSystem()
client.run(input("Token: "))
