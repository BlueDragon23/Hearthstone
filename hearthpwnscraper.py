import requests
from bs4 import BeautifulSoup
import shutil


def download_images(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    for link in soup.find_all('img'):
        pic = requests.get(link.get('src'), stream=True)
        if pic.status_code == 200:
            with open(link.get('data-href')[1:] + ".png", 'wb') as f:
                pic.raw.decode_content = True
                shutil.copyfileobj(pic.raw, f)


if __name__ == "__main__":
    for i in range(1, 7):
        url = "http://www.hearthpwn.com/cards/minion?display=3&filter-premium=1&page={}".format(i)
        download_images(url)
    for i in range(1, 3):
        url = "http://www.hearthpwn.com/cards/ability?display=3&filter-premium=1&page={}".format(i)
        download_images(url)
