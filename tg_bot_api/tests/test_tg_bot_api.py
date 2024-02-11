import os

import pytest
from dotenv import load_dotenv

from tg_bot_api.tg_bot_api import TgBotApi, TgBotApiException, TgBotClient

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")
TEST_ID = os.getenv("TEST_CHAT_ID")


def test_tg_bot_api():
    new = TgBotClient(URL, TOKEN)
    response = new.get_updates()
    assert response[0]["update_id"]
    new.check_the_user(response)
    assert len(new.allowed_users) > 0
    print("Tests for Telegram Bot API passed")


def test_raise_http_exception():
    with pytest.raises(TgBotApiException) as err:
        new = TgBotApi(URL, "hello-world")
        new.get_updates()
    assert str(err.value) == (
        "HTTPError is occured, "
        "and it is 404 Client Error: "
        "Not Found for url: "
        "https://api.telegram.org/"
        "bothello-world/getUpdates"
    )
    print("Test passed, HTTP error is occured")


"""
def test_max_redirects():
    with pytest.raises(TgBotApiException) as err:
        url = 'https://2866-79-101-225-134.ngrok-free.app/redirect_error'
        new = TgBotApi(url, TOKEN)
        new.get_updates()
    assert str(err.value) == 'Sorry, too many redirects'


def test_timeout():
    with pytest.raises(TgBotApiException) as err:
        url = 'https://2866-79-101-225-134.ngrok-free.app/timeout_error'
        new = TgBotApi(url, TOKEN)
        new.get_updates()
    assert str(err.value) == 'Timeout error. Try again later.'
"""


# К сожалению, фактически в тесте нет смысла
# Нет доступного ресурса, который бы по ссылке
# {...}/getUpdates выдавал бы не 404, а просто
# невалидный JSON
"""
def test_json_parse():
    with pytest.raises(TgBotApiException) as err:
        new = TgBotApi('https://validator.w3.org/images/w3c.png', token='')
        new.get_updates()
    print(err.value)
"""


def test_connection():
    with pytest.raises(TgBotApiException) as err:
        new = TgBotApi("https://gooogle.com/404", TOKEN)
        new.get_updates()
    assert str(err.value) == "Connection is lost, try again later."
    print("Tests passed. Connection exception is caught")


def test_send_message():
    new = TgBotApi(URL, TOKEN)
    new.get_updates()
    text = "Test passed"
    response = new.send_the_message(TEST_ID, text)
    assert response["ok"] is True
    print("Message is sent, test passed")


def test_bot_introduction():
    new = TgBotApi(URL, TOKEN)
    response = new.who_am_i()
    assert "Telegram Bot API" in response
    assert response.endswith("backend_dev_roadmap_tg_api_bot.")
    print("Bot is recognized. Test is passed")
