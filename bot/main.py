from bot.config import MOCK_MODE
if MOCK_MODE:
    from bot.pivpn_manager_mock import PiVPNManager
else:
    from bot.pivpn_manager import PiVPNManager

from bot.telegram_bot import TelegramBot

if __name__ == "__main__":
    pivpn_manager = PiVPNManager()
    bot = TelegramBot(pivpn_manager)  # pass pivpn_manager here!
    bot.run()
