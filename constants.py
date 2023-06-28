import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FORMAT = '%(asctime)s, %(levelname)s, %(name)s, %(message)s'
MUON_TEXT = (
    "What is Muon?\n\n"
    "`Muon is a decentralized oracle network that carries out data requests from any source`.\n"
    "`Muon acts as a unique inter-blockchain data-availability network that makes messaging and secure` "
    "`data interfacing possible between different chains that are otherwise incompatible`.\n\n"
    "[Muon Docs](https://docs.muon.net/muon-network/) | [Muon Explorer](https://explorer.muon.net/)"
    )
ABOUT_TEXT = (
    '*ABOUT*\r\n\n'
    '[Alex Beszedin](https://github.com/AlexBesedin) - *Python-developer (back-end)*\n'
    )
HELP_TEXT = (
    '/start - Initializing the bot\r\n'
    '/help - Information on bot commands\r\n'
    '/muon - About Muon Network\r\n'
    '/about - About the author and the project.\r\n'
    )
