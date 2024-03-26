import logging
import os
import sys
from subprocess import run

import pytest
from dotenv import load_dotenv

sys.path.insert(1, "../TgBotScripts")

from tg_bot_api import TgBotApi, TgBotApiException
from tg_bot_client import TgBotClient

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")
TEST_ID = os.getenv("TEST_CHAT_ID")
TEST_TEXT = os.getenv("TEST_TEXT")

# Пример конфигурации шаблона сообщения лога:
# Формат: время, имя уровня логирования, текст сообщения;
# Время: ДД/ММ/ГГГГ ЧЧ:ММ:СС (12-часовой формат);
# Имя лог-файла;
# Кодировка текста;
# Уровень логирования.

logging.basicConfig(
    filemode="w",
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt="%d/%m/%Y %I:%M:%S %p",
    filename="TgBotApi.log",
    encoding="utf-8",
    level=logging.INFO,
)


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
    new = TgBotClient(URL, TOKEN)
    response = new.get_updates()
    new.check_the_user(response)
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


def test_restricted_sending_message():
    with pytest.raises(TgBotApiException) as err:
        new = TgBotClient(URL, TOKEN)
        response = new.get_updates()
        new.check_the_user(response)
        new.send_the_message(12345, "You shall not receive it.")
    assert str(err.value) == "Sending messages to this user is not allowed."
    print("Tests passed. Privacy policy is under guard")


def test_tg_messenger_accessibility():
    path = "../TgBotScripts"
    command = "python3 tg_messager.py --help"
    exit_status = os.system(f"cd {path} && {command}")
    assert exit_status == 0
    print("Test is passed, CLI-util is available")


path = "../TgBotScripts"
args = f"{TOKEN} {TEST_ID}"


def test_tg_messager_with_text():
    text = "abra-kadabra"
    command = f"python3 tg_messager.py {args} -t={text}"
    exit_status = os.system(f"cd {path} && {command}")
    assert exit_status == 0
    print("Test is passed, text from CLI is sent")


def test_tg_messager_with_file():
    with open(f"{path}/text_file", "w") as file:
        file.write(TEST_TEXT)
    command = f"python3 tg_messager.py {args} -f='text_file'"
    exit_status = os.system(f"cd {path} && {command}")
    assert exit_status == 0
    print("Test is passed, text from file is sent")


def test_tg_messager_text_exception():
    os.chdir("../TgBotScripts")
    command = f"python3 tg_messager.py {args} -f=doesnt_exist"
    result = run(command.split(), capture_output=True, text=True)
    assert 'File "doesnt_exist" does not exist.' in result.stderr
    print("Test passed. Reading file which does not exist causes error.")


def test_tg_messager_file_exception():
    os.chdir("../TgBotScripts")
    command = f"python3 tg_messager.py {args}"
    result = run(command.split(), capture_output=True, text=True)
    assert "Sending empty messages is not allowed." in result.stderr
    print("Test passed. Sending empty messages is correctly forbidden.")


def test_tg_messager_restricted_user_exception():
    os.chdir("../TgBotScripts")
    command = f"python3 tg_messager.py {TOKEN} 112233 -t=text"
    result = run(command.split(), capture_output=True, text=True)
    assert "Sending messages to this user is forbidden." in result.stderr
    print("Test passed. Sending people messages without permission is correctly forbidden.")
