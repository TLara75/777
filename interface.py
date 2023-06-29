import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import engine, add_user, check_user
class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.interface)

        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.users = []
        self.offset = 0
        self.keys = []

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def missing_user_data(self, event):
        if self.params['name'] is None:
            self.message_send(event.user_id, 'Укажите Ваше имя и фамилию:')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return event.text

        elif self.params['sex'] is None:
            self.message_send(event.user_id, 'Укажите Ваш пол (1-ж, 2-м):')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return int(event.text)

        elif self.params['city'] is None:
            self.message_send(event.user_id, 'Укажите Ваш город:')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return event.text

        elif self.params['age'] is None:
            self.message_send(event.user_id, 'Введите дату рождения (дд.мм.гггг):')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return self.vk_tools.bdate_toage(event.text)

    def photo_for_user(self, user):
        photos = self.vk_tools.get_photos(user['id'])
        photo_str = ''
        for p in photos:
            photo_str += f'photo{p["owner_id"]}_{p["id"]},'
        return photo_str

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    if self.params["name"] is None:
                        self.message_send(event.user_id, 'Здравствуй')
                    else:
                        self.message_send(event.user_id, f'Здравствуй {self.params["name"]}')
                    # Недостающие данные
                    self.keys = self.params.keys()
                    for i in self.keys:
                        if self.params[i] is None:
                            self.params[i] = self.missing_user_data(event)

                    self.message_send(event.user_id,
                                      'Ваши данные имеются,'
                                      ' для поиска анкет набери "поиск" ')

                elif command == 'поиск':
                    self.message_send(event.user_id, 'Начинаю поиск...')
                    while True:
                        if self.users:
                            user = self.users.pop()
                            if check_user(engine, event.user_id, user['id']) is False:
                                add_user(engine, event.user_id, user['id'])
                                break
                        else:
                            self.users = self.vk_tools.serch_users(self.params, self.offset)

                    photo_str = self.photo_for_user(user)
                    self.offset += 10

                    self.message_send(event.user_id,
                                      f'Посмотри {user["name"]} страница vk.com/id{user["id"]}',
                                      attachment=photo_str
                                      )
                elif command == 'пока':
                    self.message_send(event.user_id, 'Досвидания')
                else:
                    self.message_send(event.user_id, 'Команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
