import logging
import requests
import sqlite3
import telebot
from utils import check, get_connection
from constants import TELEGRAM_TOKEN, FORMAT


logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
        filename='main.log',
        encoding='utf-8'
    )
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создаем таблицу, если она не существует
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

    # Получаем новое соединение
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
        bot.send_message(chat_id=message.chat.id, text=f'Hello, {username}!\n\n*Enter the IP-address of your node:*\n\n''_Example_: 99.99.999.99', parse_mode='Markdown')
    except Exception as e:
        logger.error(f'An error occurred in the /start command handler: {str(e)}')
    cursor.close()
    conn.close()


@bot.message_handler(commands=['help'])
def start_command_handler(message):
    """Обработчик команды /about"""
    bot.send_message(chat_id=message.chat.id, 
                     text=f'/start - Initializing the bot\r\n'
                     "/help - Information on bot commands\r\n"
                     "/muon - About Muon Network\r\n"
                     "/about - About the author and the project.\r\n",
                     parse_mode='Markdown'
                     )


@bot.message_handler(commands=['about'])
def start_command_handler(message):
    """Обработчик команды /help"""
    bot.send_message(chat_id=message.chat.id, 
                     text=f'*ABOUT*\r\n\n'
                     '*Author*: [Alex Beszedin](https://github.com/AlexBesedin)\n'
                     '*Open source*: [Muon Nodes checker](https://github.com/AlexBesedin/muon_nodes_checker)',
                     parse_mode='Markdown'
                     )
    

@bot.message_handler(commands=['muon'])
def muon_command_handler(message):
    """Обработчик команды /muon"""
    bot.send_message(chat_id=message.chat.id,
                     text="What is Muon?\n\n"
                          "`Muon is a decentralized oracle network that carries out data requests from any source`.\n"
                          "`Muon acts as a unique inter-blockchain data-availability network that makes messaging and secure` "
                          "`data interfacing possible between different chains that are otherwise incompatible`.\n\n"
                          "[Muon Docs](https://docs.muon.net/muon-network/) | [Muon Explorer](https://explorer.muon.net/)",
                     parse_mode='Markdown'
                     )


@bot.message_handler(func=lambda message: True)
def text_message_handler(message):
    """Данная функция является обработчиком текстовых сообщений, которые не являются командами."""
    global ip_address
    ip_address = message.text.strip()
    if check(ip_address):
        bot.send_message(chat_id=message.chat.id, 
                         text="The format of the IP address is incorrect. Please try again."
                         )
    else:
        try:
            response = requests.get(f"http://{ip_address}:8000/status", timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                manager_contract = json_data.get('managerContract', {})
                network_info = manager_contract.get('network', '')
                staker_info = json_data.get('staker', '')
                node_address_info = json_data.get('address', '')
                perr_id_info = json_data.get('peerId', '')
                network = json_data.get('network', {})
                node_info = network.get('nodeInfo', {})
                node_id = node_info.get('id', '')
                node_active = node_info.get('active', '')
                node_id_link = f"[{node_id}](https://explorer.muon.net/nodes/{node_id})"
                bot.send_message(chat_id=message.chat.id, 
                                 text=f"👤Node ID: {node_id_link}\n🟢Active: {node_active}\n⚙️Network: {network_info}\n📲Staker: `{staker_info}`\n💰Node: `{node_address_info}`\n⛓Peer id: `{perr_id_info}`", parse_mode='Markdown')
            else:
                # Если запрос не выполнен успешно, отправляем сообщение об ошибке
                bot.send_message(chat_id=message.chat.id, text="Error with IP address or node is disabled.")
        except requests.exceptions.Timeout as t:
            logger.error(f'Request timed out: {str(t)}')
            # Если запрос превысил время ожидания, отправляем сообщение об ошибке
            bot.send_message(chat_id=message.chat.id, text="The request timeout has elapsed. Check if your node works or try again later.")
        except requests.exceptions.RequestException as r:
            # Если возникла другая ошибка запроса, отправляем сообщение об ошибке
            logger.error(f'Request error: {str(t)}')
            bot.send_message(chat_id=message.chat.id, text="An error occurred while executing the request. Please try again.")


def main():
    logger.info('Muon nodes checker is starting...')
    try:
        bot.polling()
    except Exception as e:
        logger.error(f'An error occurred while running the bot: {str(e)}')


if __name__ == '__main__':
    main()