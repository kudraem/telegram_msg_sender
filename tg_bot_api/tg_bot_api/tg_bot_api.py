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
        self.update_id = None
        self.allowed_users = []

    def make_request(self, method, path, **kwargs):
        try:
            response = self.request(method, path, **kwargs,
                                    timeout=self.timeout)
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

    def check_the_user(self, response):
        for message in response:
            message_attribs = message.get('message')
            message_text = message_attribs.get('text')
            chat_id = message_attribs.get('chat').get('id')
            if (message_text == '/start'
                    and chat_id not in self.allowed_users):
                self.allowed_users.append(chat_id)

    # Либо это не документировано, либо я этого не нашел:
    # Если интервал между запросами к серверу менее 5 секунд,
    # Сервер отвечает только самым первым сообщением, отправленным
    # пользователем боту. Наиболее вероятно, что это сообщение -
    # '/start'. Это удобно для проверки, разрешил ли пользователь
    # работу нашего бота (и отправку ему сообщений в ответ).

    def get_updates(self, updates_amount=5):
        params = {'limit': updates_amount, 'offset': self.update_id}
        url = f'{self.url}{self.token}/getUpdates'
        try:
            response = self.make_request('get', url, params=params)['result']
        except KeyError:
            return TgBotApiException(
                'Something went wrong with server\'s response.')
        self.update_id = response[-1].get('update_id')
        self.check_the_user(response)
        return response

    def send_the_message(self, chat_id, text):
        if chat_id in self.allowed_users:
            params = {'chat_id': chat_id,
                      'text': text}
            url = f'{self.url}{self.token}/sendMessage'
            response = self.make_request('post', url, params=params)
            return response
