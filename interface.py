# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine
from config import comunity_token, acces_token, db_url_object
from core import VkTools
from data_store import engine, Tools, user_check, add_bd_user

class BotInterface():

    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.params = None
        self.offset = 0
        self.users = []


    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )
        
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        command = event.text.lower()
                        if command == 'привет':
                            self.params = self.api.get_profile_info(event.user_id)
                            self.message_send(event.user_id, f'Здравствуй {self.params["name"]}, я бот Василий, введите "поиск" и я начну искать Вам пару')
                            # Проверка города и даты рождения
                        elif not self.params['city'] or not self.params['bdate']:
                            if not self.params['city']:
                                self.message_send(event.user_id, f"{self.params['name']}, Введите город")
                                city = event.text.lower()
                                self.message_send(event.user_id, city)
                                self.params['city'] = city.capitalize()
                            else:
                                self.message_send(event.user_id, f"{self.params['name']}, Город уже существует")
                            if not self.params['bdate']:
                                self.message_send(event.user_id, f"{self.params['name']}, Введите Вашу дату рождения в формате ДД.ММ.ГГГГ")
                                bdate = event.text
                                self.message_send(event.user_id, bdate)
                                self.params['bdate'] = bdate
                            else:
                                self.message_send(event.user_id, f"{self.params['name']}, Дата рождения существует")
                        elif command == 'поиск':
                            if self.users:
                                self.users = self.users.pop()
                                photos = self.api.get_photos(self.users['id'])
                                photo_string = ''.join(
                                    f'photo{photo["owner_id"]}{photo["id"]}'
                                    for photo in photos
                                )
                            else:
                                    self.users = self.api.search_users(
                                self.params, self.offset)
                            self.users = self.users.pop()
                            photos = self.api.get_photos(self.users['id'])
                            photo_string = ''.join(
                                f'photo{photo["owner_id"]}_{photo["id"]},'
                                for photo in photos
                            )
                            self.offset += 10
                            self.message_send(event.user_id,f'Имя: {self.users["name"]} ссылка: vk.com/{self.users["id"]}',
                            attachment=photo_string
                            )
                            # Проверка и добавление в бд
                            if user_check(engine, event.user_id, self.users["id"]) is False:
                                add_bd_user(engine, event.user_id, self.users["id"])
                    elif command == 'пока':
                        self.message_send(event.user_id, 'Плка')
                    else:
                        self.message_send(event.user_id, 'Я знаю только команды - привет, поиск и пока')



if __name__ == '__main__':
    bot= BotInterface(comunity_token, acces_token)
    bot.event_handler()
    engine = create_engine(db_url_object)

            

