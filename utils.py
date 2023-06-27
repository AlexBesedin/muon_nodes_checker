import ipaddress
import logging
import sqlite3


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