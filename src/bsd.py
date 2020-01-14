import asyncio
import bs4
import requests


class SnowAlertSystem:

    last = ""
    ANNOUNCEMENTS = 500749047364321344

    def __init__(self, client):
        SnowAlertSystem.last = self.get_warning() 
        self.client = client

    @staticmethod
    def text_from_html(body):
        soup = bs4.BeautifulSoup(body, "html.parser")
        text = soup.find(class_="sitewide-alert").get_text()
        return text

    @staticmethod
    def get_warning():
        return SnowAlertSystem.text_from_html(requests.get("http://bsd405.org").text)

    async def check_bsd(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            if SnowAlertSystem.get_warning() != SnowAlertSystem.last:
                SnowAlertSystem.last = SnowAlertSystem.get_warning()
                await self.client.get_channel(SnowAlertSystem.ANNOUNCEMENTS).send(
                    "```{0}```".format(SnowAlertSystem.last.strip())
                )
            await asyncio.sleep(5)
