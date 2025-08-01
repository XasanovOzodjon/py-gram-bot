import time
import requests

from .types import Update
from .dispatcher import Dispatcher


class Updater:

    def __init__(self, token):
        self.token = token
        self.dispatcher = Dispatcher()
        self.offset = 0
        self.user_ids = set()  # Barcha foydalanuvchilar IDlari

    def get_udpates(self):
        payload = {
            'offset': self.offset
        }
        url = f'https://api.telegram.org/bot{self.token}/getUpdates'
        r = requests.get(url=url, params=payload)

        updates: list[Update] = []
        for row_update in r.json()['result']:
            self.offset = row_update['update_id'] + 1  # Offsetni yangilash
            updates.append(Update(
                row_update.get('message')
            ))
        return updates

    def send_message(self, chat_id, text):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        requests.post(url, data=payload)

    def send_photo(self, chat_id, photo_id):
        url = f'https://api.telegram.org/bot{self.token}/sendPhoto'
        payload = {
            'chat_id': chat_id,
            'photo': photo_id
        }
        requests.post(url, data=payload)

    def send_video(self, chat_id, video_id):
        url = f'https://api.telegram.org/bot{self.token}/sendVideo'
        payload = {
            'chat_id': chat_id,
            'video': video_id
        }
        requests.post(url, data=payload)

    def send_voice(self, chat_id, voice_id):
        url = f'https://api.telegram.org/bot{self.token}/sendVoice'
        payload = {
            'chat_id': chat_id,
            'voice': voice_id
        }
        requests.post(url, data=payload)

    def start_polling(self):
        while True:
            for update in self.get_udpates():
                msg = update.message
                if msg and 'chat' in msg:
                    user_id = msg['chat']['id']
                    self.user_ids.add(user_id)  # Foydalanuvchini ro'yxatga olish

                    # Matnli xabar
                    if 'text' in msg:
                        for uid in self.user_ids:
                            self.send_message(uid, msg['text'])

                    # Rasm (photo)
                    elif 'photo' in msg:
                        # Telegramda photo - bu ro'yxat, eng oxirgisini olish kerak (eng yuqori sifatli)
                        photo_id = msg['photo'][-1]['file_id']
                        for uid in self.user_ids:
                            self.send_photo(uid, photo_id)

                    # Video
                    elif 'video' in msg:
                        video_id = msg['video']['file_id']
                        for uid in self.user_ids:
                            self.send_video(uid, video_id)

                    # Ovozli xabar (voice)
                    elif 'voice' in msg:
                        voice_id = msg['voice']['file_id']
                        for uid in self.user_ids:
                            self.send_voice(uid, voice_id)

            time.sleep(1)


