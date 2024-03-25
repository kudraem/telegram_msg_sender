import logging

from tg_bot_api import TgBotApi, TgBotApiException


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
        self.write_users_to_file(updated)

    def write_users_to_file(self, update_status):
        report_message = "Allowed users list updated"
        with open(r".users_list", "w") as users_list:
            for user_id in self.allowed_users:
                users_list.writelines(str(user_id) + "\n")
            if update_status:
                logging.info(report_message)

    def send_the_message(self, chat_id, text):
        if chat_id in self.allowed_users:
            return super().send_message(chat_id, text)
        else:
            raise TgBotApiException(
                "Sending messages to this user is not allowed."
            )
