import re
import requests
from pydeezer import Deezer
from bs4 import BeautifulSoup

class DeezerARL:
    def __init__(self, type, arl, expiration):
        self.type = type
        self.arl = arl
        self.expiration = expiration.replace('-', '/')

    def __str__(self):
        return f"Tipo: {self.type}\n Caducidad: {self.expiration}\n```{self.arl}```\n"

    def print_arl(self):
        return self.arl


def is_valid_user(id, image):
    return id not in [None, 0] and image not in ["'https://e-cdns-images.dzcdn.net/images/user/250x250-000000-80-0-0.jpg'"]


def get_arl(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(class_='ntable')

    deezer = Deezer()
    arl = None

    for element in elements:
        rows = element.find_all('tr')
        for row in rows:
            columns = [column.text for column in row.find_all('td')[1:-1]]  # Skip the first column
            if len(columns) < 3:
                continue

            type = columns[0].strip()
            if re.match(r'^[A-Za-z\s]+$', type) and type in ['Deezer Premium','Deezer Family']:

                arl = str(columns[2]).strip()
                expiration = columns[1].strip()

                if arl and expiration:
                    deezer_arl = DeezerARL(type, arl, expiration)
                    user_info = deezer.login_via_arl(arl)
                    if is_valid_user(user_info.get("id"),user_info.get("image") ):
                        arl = deezer_arl
                    else:
                        print("Not valid user" + "")

    return arl

# Use the function
telegram_message = get_arl('https://rentry.org/firehawk52#deezer-arls')