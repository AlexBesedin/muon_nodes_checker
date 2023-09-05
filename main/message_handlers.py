import logging
import telebot
from sentry_sdk.integrations.logging import LoggingIntegration
from utils import (
    get_status, 
    get_connection,
    check_user_in_database,
    add_user_to_database,
    send_welcome_message,
    send_welcome_image,
    check_ip_address,
    get_node_info,
    parse_node_data)
from constants import (
    TELEGRAM_TOKEN, 
    FORMAT,
    HELP_TEXT,
    ABOUT_TEXT,
    MUON_TEXT)


sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Уровень логирования для отправки в Sentry
    event_level=logging.ERROR  # Уровень событий, которые будут отправляться в Sentry
)


logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    filename='main.log',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def handle_start(message):
    user_id = message.from_user.id
    try:
        with get_connection() as conn:
            if not check_user_in_database(conn, user_id):
                add_user_to_database(conn, user_id)
            username = message.from_user.username
            send_welcome_message(bot, message.chat.id, username)
            send_welcome_image(message.chat.id)
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
    

def handle_status(message):
    """Обработчик команды /status"""
    status_message = get_status()
    bot.send_message(
        chat_id=message.chat.id, 
        text=status_message)
    

def handle_text_message(message):
    """Обработчик текстовых сообщений"""
    ip_address = message.text.strip()
    check_ip_address(message, ip_address)
    response = get_node_info(ip_address, message)
    if response:
        message_text = parse_node_data(response)
        bot.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode='Markdown')
