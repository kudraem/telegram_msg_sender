import logging

import requests


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
            raise TgBotApiException("Connection is lost, try again later.")
        except requests.RequestException as err:
            raise TgBotApiException(err)

    def unpack_response_text(self, http_method, api_method, **kwargs):
        response = None
        try:
            response = self.make_request(http_method, api_method, **kwargs)
            return response["result"]
        except KeyError:
            if not response:
                logging.exception(
                    "Response is received from server, but it is empty."
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
        response = self.unpack_response_text("get", api_method)
        first_name = response.get("first_name")
        username = response.get("username")
        return (
            f"Hello. I am bot. My name is {first_name}. "
            f"You can find me at https://t.me/{username}."
        )

    def get_updates(self, updates_amount=None):
        params = {"limit": updates_amount, "offset": self.update_id}
        api_method = "getUpdates"
        response = self.unpack_response_text("get", api_method, params=params)
        # self.update_id = response[-1].get("update_id")
        return response

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        api_method = "sendMessage"
        response = self.make_request("post", api_method, params=params)
        return response
