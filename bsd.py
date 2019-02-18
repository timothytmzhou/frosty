import requests
import bs4
import asyncio
import discord


class SnowAlertSystem:
    last = ""
    ANNOUNCEMENTS = discord.Object(id=500749047364321344)

    def __init__(self, client):
        SnowAlertSystem.last = SnowAlertSystem.get_warning()
        self.client = client

    @staticmethod
    def text_from_html(body):
        soup = bs4.BeautifulSoup(body, 'html.parser')
        text = soup.find(class_="cs-column-text emergency-alert-header").get_text()
        return text

    @staticmethod
    def get_warning():
        return SnowAlertSystem.text_from_html(requests.get("http://bsd405.org").text)

    async def check_bsd(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed:
            if SnowAlertSystem.get_warning() != SnowAlertSystem.last:
                last = SnowAlertSystem.get_warning()
                await self.client.send_message(
                    SnowAlertSystem.ANNOUNCEMENTS,
                    "`{0}`".format(last.strip())
                )
            await asyncio.sleep(5)
