import argparse

from tg_bot_client import TgBotApiException, TgBotClient

parser = argparse.ArgumentParser(
    description="A utility for sending messages "
    "to the Telegram user on behalf of the bot."
)
parser.add_argument("token", type=str, help="Access token to Telegram bot.")
parser.add_argument(
    "chat_id",
    type=str,
    help="ID of chat with user, to whom the message is being sent.",
)
parser.add_argument(
    "--text", "-t", type=str, help="Text of message which is being sent."
)
parser.add_argument(
    "--file", "-f", type=str, help="Path to file with message text."
)
parser.add_argument(
    "--url",
    "-u",
    default="https://api.telegram.org/bot",
    type=str,
    help="Telegram bot URL. Argument is optional, "
    "to change default url use flags '-u' or '--url'",
)
arguments = parser.parse_args()


def send_message(url, token, chat_id, text=None, path=None):
    client = TgBotClient(url, token)
    message = None
    if text:
        message = arguments.text
    if path:
        try:
            file = open(path, "r")
        except IOError:
            print(f'File "{path}" does not exist.')
            return
        message = file.read()
    try:
        client.send_the_message(int(chat_id), message)
    except TgBotApiException:
        if message is None:
            raise TgBotApiException(
                "Sending empty messages is not allowed. "
                'Use "-t" or "--text" flags for sending text from stdin, '
                '"-f" of "--file" flags for input path to file with text, '
                '"-h" or "--help" flags for getting help.'
            )
        raise TgBotApiException(
            "Sending messages to this user is forbidden. "
            "Check whether the user is in list of allowed users."
        )


send_message(
    arguments.url,
    arguments.token,
    arguments.chat_id,
    arguments.text,
    arguments.file,
)
