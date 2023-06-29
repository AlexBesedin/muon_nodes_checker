import os
import logging
import requests
import sqlite3
import telebot
from datetime import datetime
from bs4 import BeautifulSoup
from utils import check, get_connection
from constants import (TELEGRAM_TOKEN, FORMAT, 
                       MUON_TEXT, ABOUT_TEXT, 
                       HELP_TEXT, MUON_URL, LINKS_NODE_ID,
                       TIMEOUT_ERROR, REQUEST_ERROR)


logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    filename='main.log',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

with sqlite3.connect('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, 
                      interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                   '''
                   )
    conn.commit()


@bot.message_handler(commands=['start'])
def start_command_handler(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
            "*Enter the IP-address of your node:*\n\n"
            "_Example:_"
        )
        bot.send_message(chat_id=message.chat.id,
                         text=message_text,
                         parse_mode='Markdown'
                         )
        image_path = os.path.join('pic', 'picpic.jpg')
        with open(image_path, 'rb') as image:
            bot.send_photo(chat_id=message.chat.id, 
                           photo=image
                           )
    except Exception as e:
        logger.error(f'An error occurred in the /start command handler: {str(e)}')
    finally:
        cursor.close()
        conn.close()


@bot.message_handler(commands=['help'])
def help_command_handler(message):
    """Обработчик команды /help"""
    bot.send_message(chat_id=message.chat.id,
                     text=HELP_TEXT,
                     parse_mode='Markdown'
                     )


@bot.message_handler(commands=['about'])
def about_command_handler(message):
    """Обработчик команды /about"""
    bot.send_message(chat_id=message.chat.id,
                     text=ABOUT_TEXT,
                     parse_mode='Markdown'
                     )


@bot.message_handler(commands=['muon'])
def muon_command_handler(message):
    """Обработчик команды /muon"""
    bot.send_message(chat_id=message.chat.id,
                     text=MUON_TEXT,
                     parse_mode='Markdown'
                     )
    

@bot.message_handler(commands=['status'])
def muon_command_handler(message):
    """Обработчик команды /status"""
    status_message = get_status()
    bot.send_message(chat_id=message.chat.id, text=status_message)    
               

@bot.message_handler(func=lambda message: True)
def text_message_handler(message):
    ip_address = message.text.strip()
    status_message = get_status()
    if ip_address == '/status':
        bot.send_message(
            chat_id=message.chat.id, 
            text=status_message
            )
    elif check(ip_address):
        bot.send_message(
            chat_id=message.chat.id, 
            text="The format of the IP address is incorrect. Please try again."
            )
    else:
        try:
            response = requests.get(f"http://{ip_address}:8000/status", timeout=50)
            if response.status_code == 200:
                json_data = response.json()
                manager_contract = json_data.get('managerContract', {})
                node_cont = json_data.get('node', {})
                uptime_info = node_cont.get('uptime', '')
                networking_port = node_cont.get('networkingPort', '')
                network_info = manager_contract.get('network', '')
                staker_info = json_data.get('staker', '')
                node_address_info = json_data.get('address', '')
                perr_id_info = json_data.get('peerId', '')
                network = json_data.get('network', {})
                node_info = network.get('nodeInfo', {})
                node_id = node_info.get('id', '')
                node_active = node_info.get('active', '')
                node_id_link = f"[{node_id}](https://explorer.muon.net/nodes/{node_id})"

                try:
                    links_nodes = LINKS_NODE_ID + f'{node_id}'
                    session = requests.Session()
                    response = session.get(links_nodes)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.text, features='lxml')
                    tag_div = soup.find('div', attrs={'class': 'sc-12fa1d5b-0 fQGscc card rounded-4 p-3 position-relative overflow-hidden h-100'})
                    tag_h6_list = tag_div.find_all('h6')
                    uptime_value = ''
                    for tag_h6 in tag_h6_list:
                        if '%' in tag_h6.text:
                            uptime_value = tag_h6.text
                            break
                except Exception as e:
                    logger.error(f'Error parsing id data: {str(e)}')
                    uptime_value = 'Error parsing id data'

                node_address_short = f"{node_address_info[:6]}...{node_address_info[-6:]}"
                staker_info_short = f"{staker_info[:6]}...{staker_info[-6:]}"
                perr_id_info_short = f"{perr_id_info[:6]}...{perr_id_info[-6:]}"

                message_text = (
                    f"👤 Node ID: {node_id_link}\n"
                    f"🟢 Active: {node_active}\n"
                    f"🌐 Uptime: {uptime_value}\n"
                    f"⚙️ Network: {network_info}\n"
                    f"📟 Uptime: `{uptime_info}`\n"
                    f"💰 Node: `{node_address_short}`\n"
                    f"📲 Staker: `{staker_info_short}`\n"
                    f"⛓ Peer id: `{perr_id_info_short}`\n"
                    f"🔋 NetworkingPort: `{networking_port}`\n"
                )
                bot.send_message(chat_id=message.chat.id,
                                 text=message_text,
                                 parse_mode='Markdown'
                                 )
            else:
                # Если запрос не выполнен успешно, отправляем сообщение об ошибке
                bot.send_message(chat_id=message.chat.id,
                                 text="Error with IP address or node is disabled."
                                 )
        except requests.exceptions.Timeout as t:
            logger.error(f'Request timed out: {str(t)}')
            # Если запрос превысил время ожидания, отправляем сообщение об ошибке
            bot.send_message(chat_id=message.chat.id,
                             text=TIMEOUT_ERROR
                             )
        except requests.exceptions.RequestException as r:
            # Если возникла другая ошибка запроса, отправляем сообщение об ошибке
            logger.error(f'Request error: {str(r)}')
            bot.send_message(chat_id=message.chat.id,
                             text=REQUEST_ERROR
                             )
            

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


def main():
    logger.info('Muon nodes checker is starting...')
    try:
        bot.polling()
    except Exception as e:
        logger.error(f'An error occurred while running the bot: {str(e)}')


if __name__ == '__main__':
    main()
