import requests
import bs4


class SnowAlertSystem:
    last = ""

    def __init__(self):
        SnowAlertSystem.last = SnowAlertSystem.get_warning()

    @staticmethod
    def text_from_html(body):
        soup = bs4.BeautifulSoup(body, 'html.parser')
        text = soup.find(class_="cs-column-text emergency-alert-header").get_text()
        return text

    @staticmethod
    def get_warning():
        return SnowAlertSystem.text_from_html(requests.get("http://bsd405.org").text)
