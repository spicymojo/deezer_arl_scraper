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

def get_arl_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(class_='ntable')

    printed_rows = 0
    rows_to_print = 1
    deezer = Deezer()
    arl_list = []

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
                    if printed_rows < rows_to_print:
                        printed_rows += 1
                        user_info = deezer.login_via_arl(deezer_arl.arl)
                        if user_info.get("arl"):
                            arl_list.append(deezer_arl)
    return arl_list

# Use the function
telegram_message = get_arl_list('https://rentry.org/firehawk52#deezer-arls')