import requests
from decleverett import Config, Param

from .base import Notifier


class TelegramConfig(Config):
    namespace = "telegram"
    TOKEN = Param()
    CHATS = Param()


class TelegramNotifier(Notifier):
    TELEGRAM_API = "https://api.telegram.org/bot{}"

    def __init__(self, chats: str = None, token: str = None):
        self.chats = chats
        self.token = token

    @property
    def chats_(self):
        try:
            return (self.chats or TelegramConfig.CHATS).split(",")
        except AttributeError:
            pass
        return

    @property
    def token_(self):
        return self.token or TelegramConfig.TOKEN

    @property
    def telegram_api(self):
        return self.TELEGRAM_API.format(self.token_)

    def notify(self, msg):
        if self.token_ is None:
            return
        if self.chats_ is None:
            raise ValueError(
                "Set TELEGRAM_CHATS to comma-separated list of chat ids. "
                f"Find them out at {self.TELEGRAM_API}<token>/getUpdates"
            )
        for chat_id in self.chats_:
            requests.post(
                f"{self.telegram_api}/sendMessage",
                json={"chat_id": chat_id, "text": msg},
            ).raise_for_status()
