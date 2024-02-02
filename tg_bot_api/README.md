### Скрипт взаимодействия с телеграм-ботом [Telegram Bot API](https://github.com/nickitey/backend_dev_roadmap/tree/main/projects/telegram_notification_service/sprint_2) на Python.

Взаимодействие с чат-ботом в Telegram реализовано в классе *TgBotApi*, отнаследованном от класса *requests.Session*, в связи с чем для работы требует установленный модуль *requests*.

Скрипт предоставляет возможность работы с телеграм-ботом посредством http-запросов к Telegram Bot API путем создания экземпляра класса и использования доступных методов:

1. **who_am_i()**:

*Аргументы*: не требуются.
    
*Возвращает*: строку формата 
        
```python
    Hello. I am bot. My name is {first_name}. You can find me at https://t.me/{username}.
```
    
    
2. **get_updates(**[updates_amount=5: **int**]**)**:

*Аргументы*: необязательный аргумент updates_amount: *int* - количество последних апдейтов бота (входящие, исходящие сообщения).
    
*Возвращает*: список словарей формата
    
```python
    [
        {
        'update_id': int, 
        'message': {
            'message_id': int, 
            'from': 
    	        {'id': int, 'is_bot': False, 'first_name': 'str', 'last_name': 'str', 'username': 'str', 'language_code': 'ru'}, 
            'chat': 
    	        {'id': str, 'first_name': 'str', 'last_name': 'str', 'username': 'str', 'type': 'private'}, 
            'date': int(UNIX time), 
            'text': 'str', 
            'entities':
    	        [{'offset': 0, 'length': 6, 'type': 'bot_command'}] 
            }
        }
     ...
     ]
```
Полный список возможных параметров словаря доступен в документации: общее описание объекта [ответа](https://core.telegram.org/bots/api#update), описание объекта [сообщения](https://core.telegram.org/bots/api#message).

Метод также проверяет, кто из пользователей нажал сервисную кнопку ```/start``` в боте, чтобы занести id чата с данным пользователем в список тех, кому бот может отправлять сообщения.
	 
3. **send_the_message(** chat_id: **int**, text: **str)**:

*Аргументы*: id чата бота с пользователем[^1], текст сообщения к отправке.

[^1]: Его можно получить из апдейтов.

*Возвращает*: объект ответа, который практического значения для пользователя не имеет.
        
Сообщение будет отправлено пользователю только в том случае, если id чата с ним занесен в список тех, кому бот может отправлять сообщения[^2]. 

[^2]: Смотри описание метода get_updates()
