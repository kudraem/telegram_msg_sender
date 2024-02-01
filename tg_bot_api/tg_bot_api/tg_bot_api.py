import requests


class TgBotApiException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TgBotApi(requests.Session):
    def __init__(self):
        super().__init__()
        self.max_redirects = 5
        self.headers = {'User-Agent': 'Python-Study-App/1.0.0',
                        'Content-Type': 'application/json'}
        self.timeout = 5.0

    def get_bot_username(self):
        return "Telegram Bot API"

    def get_bot_token(self):
        return '6929213342:AAGQHDN--h2bg7k2IT-s019317WdmICQ0D4'

    def on_update_received(self, update):
        return update

