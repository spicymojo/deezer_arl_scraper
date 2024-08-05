import re
import requests
from pydeezer import Deezer
from bs4 import BeautifulSoup

class DeezerARL:
    def __init__(self, type, arl, expiration):
        self.type = type
        self.arl = arl
        self.expiration = expiration  # Store expiration as a string

    def __str__(self):
        return f"Type: {self.type}, ARL: {self.arl},Expiration: {self.expiration}"

def print_arl(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(class_='ntable')

    rows_to_print = 0
    deezer = Deezer()

    for element in elements:
        rows = element.find_all('tr')
        for row in rows:
            columns = [column.text for column in row.find_all('td')[1:-1]]  # Skip the first column
            if len(columns) < 3:
                continue

            type = columns[0].strip()
            if re.match(r'^[A-Za-z\s]+$', type) and type in 'Deezer Premium':

                arl = str(columns[2]).strip()
                expiration = columns[1].strip()

                if arl and expiration:
                    deezer_arl = DeezerARL(type, arl, expiration)
                    if rows_to_print < 5:
                        rows_to_print += 1
                        user_info = deezer.login_via_arl(deezer_arl.arl)
                        if user_info.get("id"):
                            print(deezer_arl)

# Use the function
print_arl('https://rentry.org/firehawk52#deezer-arls')