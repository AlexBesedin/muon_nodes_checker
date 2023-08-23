import logging
import os
import telebot
import requests
from bs4 import BeautifulSoup
from utils import check, get_status, get_connection
from constants import (
    LINKS_NODE_ID, 
    TIMEOUT_ERROR, 
    REQUEST_ERROR, 
    TELEGRAM_TOKEN, 
    FORMAT,
    HELP_TEXT,
    ABOUT_TEXT,
    MUON_TEXT)


logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    filename='main.log',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def handle_start(message, bot, logger):
    user_id = message.from_user.id
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Проверка, существует ли пользователь уже в базе данных
            cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                # Если пользователь новый, добавляем его в базу данных
                cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                conn.commit()
            username = message.from_user.username
            message_text = (
                f"Hello, {username}!\n\n"
                "*Enter the IP-address of your Muon Node:*\n"
                "_Example:_"
            )
            bot.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode='Markdown'
            )
            image_path = os.path.join('pic', 'picpic.jpg')
            with open(image_path, 'rb') as image:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=image
                )
    except Exception as e:
        logger.error(f'An error occurred in the /start command handler: {str(e)}')


def handle_help(message):
    """Обработчик команды /help"""
    bot.send_message(
        chat_id=message.chat.id,
        text=HELP_TEXT,
        parse_mode='Markdown')
    

def handle_about(message):
    """Обработчик команды /about"""
    bot.send_message(
        chat_id=message.chat.id,
        text=ABOUT_TEXT,
        parse_mode='Markdown')
    

def handle_muon(message):
    """Обработчик команды /muon"""
    bot.send_message(
        chat_id=message.chat.id,
        text=MUON_TEXT,
        parse_mode='Markdown')
    

def handle_status(message, bot):
    """Обработчик команды /status"""
    status_message = get_status()
    bot.send_message(
        chat_id=message.chat.id, 
        text=status_message)
    

def handle_text_message(message, bot):
    """Обработчик текстовых сообщений"""
    ip_address = message.text.strip()
    if check(ip_address):
        bot.send_message(
            chat_id=message.chat.id,
            text="The format of the IP address is incorrect. Please try again.")
        return
    try:
        response = requests.get(f"http://{ip_address}:8011/status", timeout=50)

        if response.status_code == 200:
            json_data = response.json()
            node_info = json_data.get('network', {}).get('nodeInfo', {})
            node_id = node_info.get('id', '')
            node_active = node_info.get('active', '')
            node_id_link = f"[{node_id}](https://explorer.muon.net/nodes/{node_id})"
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
                    uptime_value = float(''.join(filter(str.isdigit, uptime_value))) / 100
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
                f"🟢 Active: {node_active}\n"
                f"🌐 Uptime: {uptime_value} %\n"
                f"⚙️ Network: {network_info}\n"
                f"📟 Uptime: `{uptime_info}`\n"
                f"💰 Node: `{node_address_short}`\n"
                f"📲 Staker: `{staker_info_short}`\n"
                f"⛓ Peer id: `{perr_id_info_short}`\n"
                f"🔋 NetworkingPort: `{networking_port}`\n"
            )

            bot.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode='Markdown')
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Error with IP address or node is disabled.")
    except requests.exceptions.Timeout as t:
        logger.error(f'Request timed out: {str(t)}')
        bot.send_message(
            chat_id=message.chat.id,
            text=TIMEOUT_ERROR)
    except requests.exceptions.RequestException as r:
        logger.error(f'Request error: {str(r)}')
        bot.send_message(
            chat_id=message.chat.id,
            text=REQUEST_ERROR) 
