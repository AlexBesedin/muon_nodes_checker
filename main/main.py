import logging
import telebot
from constants import TELEGRAM_TOKEN, FORMAT
from db import create_database
from message_handlers import (
    handle_start, 
    handle_help,
    handle_about,
    handle_muon,
    handle_status,
    handle_text_message)


logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    filename='main.log',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

create_database()


@bot.message_handler(commands=['start'])
def start_command_handler(message):
    """Хендлер команды /start"""
    handle_start(message)      
    

@bot.message_handler(commands=['help'])
def help_command_handler(message):
    """Хендлер команды /help"""
    handle_help(message)


@bot.message_handler(commands=['about'])
def about_command_handler(message):
    """Хендлер команды /about"""
    handle_about(message)


@bot.message_handler(commands=['muon'])
def muon_command_handler(message):
    """Хендлер команды /muon"""
    handle_muon(message)
    

@bot.message_handler(commands=['status'])
def status_command_handler(message):
    """Хендлер команды /status"""
    handle_status(message)
    

@bot.message_handler(func=lambda message: True)
def text_message_handler(message):
    """Хендлер тестовых сообщений"""
    handle_text_message(message)

            
def main():
    logger.info('Muon nodes checker is starting...')
    try:
        bot.polling()
    except Exception as e:
        logger.error(f'An error occurred while running the bot: {str(e)}')


if __name__ == '__main__':
    main()
