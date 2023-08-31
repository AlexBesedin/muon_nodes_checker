import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MUON_URL = 'https://explorer.muon.net/'
LINKS_NODE_ID = 'https://explorer.muon.net/nodes/'
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
    '[Кул стори, джун!](https://t.me/coolstoryjunior) - *Сообщество поддержки*'
    )
HELP_TEXT = (
    '/start - Initializing the bot\n'
    '/status - Muon nodes status(total number, active and inactive nodes)\n'
    '/muon - About Muon Network\n'
    '/about - About the author\n'
    '/help - Information on bot commands\n'
    )
TIMEOUT_ERROR = (
    "⚠️⚠️⚠️\nThe request timeout has elapsed.\n"
    "Check if your node works or try again later."
    )
REQUEST_ERROR = (
    "An error occurred while executing the request.\n"
    "Please try again."
)