import ipaddress
import logging
import telebot
import requests
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
from sentry_sdk.integrations.logging import LoggingIntegration
from constants import MUON_URL, TELEGRAM_TOKEN,LINKS_NODE_ID

bot = telebot.TeleBot(TELEGRAM_TOKEN)


sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Уровень логирования для отправки в Sentry
    event_level=logging.ERROR  # Уровень событий, которые будут отправляться в Sentry
)
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
        filename='main.log',
        encoding='utf-8'
    )
logger = logging.getLogger(__name__)


def check_ip_address(message, ip_address):
    """Проверяет валидность введёного IP-адреса"""
    try:
        ipaddress.ip_address(ip_address)
        print("Valid IP address")
        return False
    except ValueError as e:
        logger.error(f'Invalid IP address: {str(e)}')
        print("Invalid IP address")
        bot.send_message(
            chat_id=message.chat.id,
            text="The format of the IP address is incorrect. Please try again.")
        return True


def get_connection():
    """Возвращает объект соединения с базой данных"""
    try:
        return sqlite3.connect('users.db')
    except ConnectionError as ce:
        logger.error(f'Database connection error: {str(ce)}')


def get_status():
    """Парсит данные о всех узлах в сети и возвращает результат"""
    try:
        with requests.Session() as session:
            response = session.get(MUON_URL)
            response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, features='lxml')
        tag_div = soup.find('div', attrs={
            'class': 'card-footer border-0 bg-transparent'}
                            )
        numerical_elements = tag_div.find_all(
            'h5', class_='fw-bold mb-0 mt-2 align-self-end')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"Pion Nodes Status:\n"
        message += f"🟠 Total Nodes: {numerical_elements[0].get_text()}\n"
        message += f"🟢 Active Nodes: {numerical_elements[1].get_text()}\n"
        message += f"❌ Deactive Nodes: {numerical_elements[2].get_text()}\n"
        message += f"Data as of {current_time}\n"
        return message
    except Exception as e:
        logger.error(f'Parsing status error: {str(e)}') 


def check_user_in_database(conn, user_id):
    """Метод проверяет, есть ли юзер в БД"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None


def add_user_to_database(conn, user_id):
    """Метод добавляет юзера в БД"""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()


def send_welcome_message(bot, chat_id, username):
    """Отправка приветственного сообщения при инициализации команды /start"""
    try:
        message_text = (
            f"Hello, {username}!\n\n"
            "Enter the IP-address of your PION Node:\n"
            "Example: 94.131.107.141")
        bot.send_message(chat_id=chat_id, text=message_text)
    except Exception as e:
        logger.error(f'Send welcome message error: {str(e)}') 
        

def send_welcome_image(chat_id):
    """Отправка изображения с примером ввода IP-адреса"""
    try:
        image_path = '/app/main/pic/picpic.jpg'
        with open(image_path, 'rb') as image:
            bot.send_photo(chat_id=chat_id, photo=image)
    except Exception as e:
        logger.error(f'Send welcome image error: {str(e)}')
        logger.info(f'Image path: {image_path}')



def get_node_info(ip_address, message):
    """Получение информации о доступности ip_адреса:8012/status"""
    try:
        response = requests.get(f"http://{ip_address}:8012/status", timeout=10)
        return response
    except requests.exceptions.Timeout as t:
        logger.error(f'Request timed out: {str(t)}')
        bot.send_message(
            chat_id=message.chat.id,
            text='Connection is not established. Your node is offline now or you have entered the wrong IP address. Try again later')
        return None
    except requests.exceptions.RequestException as r:
        logger.error(f'Request error: {str(r)}')
        bot.send_message(
            chat_id=message.chat.id,
            text='Request error')
        return None
    

def parse_node_data(response):
    """Парсинг основной информации о узле"""
    if response.status_code == 200:
        json_data = response.json()
        node_info = json_data.get('network', {}).get('nodeInfo', {})
        tier_info = node_info.get('tier', '')
        node_id = node_info.get('id', '')
        node_active = node_info.get('active', '')
        node_id_link = f"[{node_id}](https://explorer.muon.net/pion/nodes/{node_id})"
        uptime_info = json_data.get('node', {}).get('uptime', '')
        networking_port = json_data.get('node', {}).get('networkingPort', '')
        network_info = json_data.get('managerContract', {}).get('network', '')
        staker_info = json_data.get('staker', '')
        node_address_info = json_data.get('address', '')
        perr_id_info = json_data.get('peerId', '')

        try:
            links_nodes = LINKS_NODE_ID + f'{node_id}'
            response = requests.get(links_nodes, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            tag_div = soup.find(
                'div', class_='number rounded-circle d-flex justify-content-center align-items-center')
            if tag_div:
                uptime_value = next(
                    (tag_h6.text for tag_h6 in tag_div.find_all('h6') if '%' in tag_h6.text), 
                    'Error parsing id data')
                uptime_value = float(''.join(filter(str.isdigit, uptime_value)))
            else:
                uptime_value = 'Error parsing id data'
        except Exception as e:
            logger.error(f'Error parsing id data: {str(e)}')
            uptime_value = 'Error parsing id data'

        node_address_short = f"{node_address_info[:6]}...{node_address_info[-6:]}"
        staker_info_short = f"{staker_info[:6]}...{staker_info[-6:]}"
        perr_id_info_short = f"{perr_id_info[:6]}...{perr_id_info[-6:]}"

        message_text = (
            f"👤 Node ID: {node_id_link}\n"
            f"📊 Tier : {tier_info}\n"
            f"🟢 Active: {node_active}\n"
            f"🌐 Uptime: {uptime_value} %\n"
            f"⚙️ Network: {network_info}\n"
            f"📟 Uptime: `{uptime_info}`\n"
            f"💰 Node: `{node_address_short}`\n"
            f"📲 Staker: `{staker_info_short}`\n"
            f"⛓ Peer id: `{perr_id_info_short}`\n"
            f"🔋 NetworkingPort: `{networking_port}`\n"
        )

        return message_text
    else:
        return "An invalid IP address or the status of your node is offline."
