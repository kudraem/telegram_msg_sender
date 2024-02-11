import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")


logging.basicConfig(
    format="\n%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="TgBotApi.log",
    encoding="utf-8",
    level=logging.INFO,
)


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
        self.headers = {
            "User-Agent": "Python-Study-App/1.0.0",
            "Content-Type": "application/json",
        }
        self.timeout = 5.0
        self.update_id = None
        self.allowed_users = []

    def make_request(self, http_method, api_method, **kwargs):
        url = f"{self.url}{self.token}/{api_method}"
        try:
            response = self.request(http_method,
                                    url, **kwargs, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.JSONDecodeError as err:
            raise TgBotApiException(
                f"Incoming JSON is invalid from char {err.pos}")
        except requests.TooManyRedirects:
            raise TgBotApiException(
                f"Too much redirects. Allowed: {self.max_redirects}."
            )
        except requests.HTTPError as err:
            raise TgBotApiException(
                f"HTTPError is occured, and it is {err}")
        except requests.Timeout:
            raise TgBotApiException(
                f"Timeout error. Request is executed over \
                {self.timeout} seconds."
            )
        except requests.ConnectionError:
            raise TgBotApiException(
                "Connection is lost, try again later.")

    def get_request_result(self, http_method, api_method, **kwargs):
        response = None
        try:
            response = self.make_request(http_method, api_method, **kwargs)
            return response["result"]
        except KeyError:
            if not response:
                logging.exception(
                    "Response is received from server, "
                    "but it is empty."
                )
            elif response["ok"] is True:
                logging.exception(
                    "Response is received from server, "
                    "but there's not any result"
                )
            else:
                logging.exception(
                    "Response is received from server,"
                    "but something is wrong with it."
                )

    def who_am_i(self):
        api_method = "getMe"
        response = self.get_request_result("get", api_method)
        first_name = response.get("first_name")
        username = response.get("username")
        return (
            f"Hello. I am bot. My name is {first_name}. "
            f"You can find me at https://t.me/{username}."
        )

    def check_the_user(self, response):
        for message in response:
            message_attribs = message.get("message")
            message_text = message_attribs.get("text")
            chat_id = message_attribs.get("chat").get("id")
            if message_text == "/start" and chat_id not in self.allowed_users:
                self.allowed_users.append(chat_id)

    # Либо это не документировано, либо я этого не нашел:
    # Если интервал между запросами к серверу менее 5 секунд,
    # Сервер отвечает только самым первым сообщением, отправленным
    # пользователем боту. Наиболее вероятно, что это сообщение -
    # '/start'. Это удобно для проверки, разрешил ли пользователь
    # работу нашего бота (и отправку ему сообщений в ответ).

    def get_updates(self, updates_amount=5):
        params = {"limit": updates_amount, "offset": self.update_id}
        api_method = "getUpdates"
        response = self.get_request_result("get", api_method, params=params)
        # self.update_id = response[-1].get("update_id")
        # self.check_the_user(response)
        return response

    def send_the_message(self, chat_id, text):
        if chat_id in self.allowed_users:
            params = {"chat_id": chat_id, "text": text}
            api_method = "sendMessage"
            response = self.make_request("post", api_method, params=params)
            return response
