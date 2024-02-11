import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt="%d/%m/%Y %I:%M:%S %p",
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

    def make_request(self, http_method, api_method, **kwargs):
        url = f"{self.url}{self.token}/{api_method}"
        try:
            response = self.request(
                http_method, url, **kwargs, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.JSONDecodeError as err:
            raise TgBotApiException(
                f"Incoming JSON is invalid from char {err.pos}"
            )
        except requests.TooManyRedirects:
            raise TgBotApiException(
                f"Too much redirects. Allowed: {self.max_redirects}."
            )
        except requests.HTTPError as err:
            raise TgBotApiException(f"HTTPError is occured, and it is {err}")
        except requests.Timeout:
            raise TgBotApiException(
                f"Timeout error. Request is executed over \
                {self.timeout} seconds."
            )
        except requests.ConnectionError:
            raise TgBotApiException(
                 "Connection is lost, try again later.")
        except requests.RequestException as err:
            raise TgBotApiException(err)

    def get_request_result(self, http_method, api_method, **kwargs):
        response = None
        try:
            response = self.make_request(http_method, api_method, **kwargs)
            return response["result"]
        except KeyError:
            if not response:
                logging.exception(
                    "Response is received from server, " "but it is empty."
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

    def get_updates(self, updates_amount=None):
        params = {"limit": updates_amount, "offset": self.update_id}
        api_method = "getUpdates"
        response = self.get_request_result("get", api_method, params=params)
        # self.update_id = response[-1].get("update_id")
        return response

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        api_method = "sendMessage"
        response = self.make_request("post", api_method, params=params)
        return response


class TgBotClient(TgBotApi):
    def __init__(self, url, token):
        super().__init__(url, token)
        self.url = url
        self.token = token
        self.allowed_users = []
        self.open_user_list()

    def open_user_list(self):
        try:
            with open(".users_list", "r") as users_list:
                for line in users_list:
                    user = line.strip()
                    self.allowed_users.append(int(user))
        except IOError:
            logging.error(
                "Try to open allowed users list file,"
                "but it does not exist yet."
            )

    def check_the_user(self, response):
        updated = False
        for message in response:
            try:
                message_attribs = message["message"]
            except KeyError:
                logging.error(
                    f'Update #{message.get("update_id")} '
                    f"contains no user messages but service "
                    f"information."
                )
                continue
            else:
                message_text = message_attribs.get("text")
                chat_attrib = message_attribs.get("chat")
                message_author = (
                    f"{chat_attrib.get('first_name')} "
                    f"{chat_attrib.get('last_name')}"
                )
                chat_id = chat_attrib.get("id")
                if (
                    message_text == "/start"
                    and chat_id not in self.allowed_users
                ):
                    self.allowed_users.append(chat_id)
                    logging.info(
                        f"{message_author} with id {chat_id} "
                        f"added to allowed users list"
                    )
                    updated = True
        report_message = "Allowed users list updated"
        with open(r".users_list", "w") as users_list:
            for user_id in self.allowed_users:
                users_list.writelines(str(user_id) + "\n")
            if updated:
                logging.info(report_message)

    def send_the_message(self, chat_id, text):
        if chat_id in self.allowed_users:
            return super().send_message(chat_id, text)
        else:
            raise TgBotApiException(
                'Sending messages to this user is not allowed.'
            )
