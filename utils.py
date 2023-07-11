import ipaddress
import logging
import requests
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
from constants import MUON_URL


logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
        filename='main.log',
        encoding='utf-8'
    )
logger = logging.getLogger(__name__)


def check(ip):
    try:
        ipaddress.ip_address(ip)
        print("Valid IP address")
        return False
    except ValueError as e:
        logger.error(f'Invalid IP address: {str(e)}')
        # If the input is not a valid IP address, catch the exception and return True
        print("Invalid IP address")
        return True


def get_connection():
    return sqlite3.connect('users.db')


def get_status():
    session = requests.Session()
    response = session.get(MUON_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    tag_div = soup.find('div', attrs={'class': 'card-footer border-0 bg-transparent'})
    numerical_elements = tag_div.find_all('h6', class_='fw-bold mb-0 mt-2 align-self-end')
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = '-' * 39

    message = f"Muon Nodes Status:\n"
    message += f"{separator}\n"
    message += f"🟠 Total Nodes: {numerical_elements[0].get_text()}\n"
    message += f"🟢 Active Nodes: {numerical_elements[1].get_text()}\n"
    message += f"❌ Deactive Nodes: {numerical_elements[2].get_text()}\n"
    message += f"{separator}\n"
    message += f"Data as of {current_time}\n"

    return message
