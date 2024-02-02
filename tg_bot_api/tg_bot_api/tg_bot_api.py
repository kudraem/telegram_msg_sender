import requests

URL = 'https://api.telegram.org/bot'
TOKEN = '6929213342:AAGQHDN--h2bg7k2IT-s019317WdmICQ0D4'


class TgBotApiException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TgBotApi(requests.Session):
    def __init__(self, url, token):
        super().__init__()
        self.url = url
        self.token = token
        self.max_redirects = 5
        self.headers = {'User-Agent': 'Python-Study-App/1.0.0',
                        'Content-Type': 'application/json'}
        self.timeout = 5.0

    def make_request(self, method, path, **kwargs):
        try:
            response = self.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.JSONDecodeError:
            raise TgBotApiException('Incoming JSON is invalid')
        except requests.TooManyRedirects:
            raise TgBotApiException('Sorry, too many redirects')
        except requests.HTTPError as err:
            raise TgBotApiException(f'HTTPError is occured, and it is {err}')
        except requests.Timeout:
            raise TgBotApiException('Timeout error. Try again later.')
        except requests.ConnectionError:
            raise TgBotApiException('Connection is lost, try again later.')

    def get_bot_username(self):
        return "Telegram Bot API"

    def get_updates(self):
        url = f'{self.url}{self.token}/getUpdates'
        return self.make_request('get', url)
