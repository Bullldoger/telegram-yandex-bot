"""

"""

import time
import os
import requests

import yadisk

import telebot
from IPython.utils.capture import capture_output
from telebot import types

from bot.configurator import RestConfigurator, MongoConfigurator
from bot.managers import BotMongoManager, BotRestManager


class YandexDiskBot:
    """
    # msg_template = {
    #     'content_type': 'text',
    #     'message_id': 24,
    #     'from_user': {
    #         'id': 503388409,
    #         'is_bot': False,
    #         'first_name': 'Ромаха',
    #         'username': 'loler_true',
    #         'last_name': 'Омарович',
    #         'language_code': 'en-US'
    #     },
    #     'date': 1521838101,
    #     'chat': {
    #         'type': 'private',
    #         'last_name': 'Омарович',
    #         'first_name': 'Ромаха',
    #         'username': 'loler_true',
    #         'id': 503388409,
    #         'title': None,
    #         'all_members_are_administrators': None,
    #         'photo': None,
    #         'description': None,
    #         'invite_link': None,
    #         'pinned_message': None,
    #         'sticker_set_name': None,
    #         'can_set_sticker_set': None
    #     },
    #     'forward_from_chat': None,
    #     'forward_from': None,
    #     'forward_date': None,
    #     'reply_to_message': None,
    #     'edit_date': None,
    #     'media_group_id': None,
    #     'author_signature': None,
    #     'text': '/folders',
    #     'caption_entities': None,
    #     'audio': None,
    #     'document': None,
    #     'photo': None,
    #     'sticker': None,
    #     'video': None,
    #     'video_note': None,
    #     'voice': None,
    #     'caption': None,
    #     'contact': None,
    #     'location': None,
    #     'venue': None,
    #     'new_chat_member': None,
    #     'new_chat_members': None,
    #     'left_chat_member': None,
    #     'new_chat_title': None,
    #     'new_chat_photo': None,
    #     'delete_chat_photo': None,
    #     'group_chat_created': None,
    #     'supergroup_chat_created': None,
    #     'channel_chat_created': None,
    #     'migrate_to_chat_id': None,
    #     'migrate_from_chat_id': None,
    #     'pinned_message': None,
    #     'invoice': None,
    #     'successful_payment': None,
    #     'connected_website': None
    # }
    """

    bot = None
    disk_api = None

    yandex_app_key = '724f0fc500f24e5c819d73b1c0d7c020'
    yandex_app_secret = '22bee918482c4972957f0cc34a1fbd06'
    yandex_token = 'AQAAAAATRTcCAATojgcA_0RcIkReo7pQ1qaXJ0s'
    telegram_bot_token = '596764618:AAFfnyH_s6R_u9ZPyF6OH8nZS1q-woRZeoM'

    current_path = 'disk:/'
    root_path = 'disk:/'

    special_words = {
        'back': 'back'
    }

    commands = ['start', 'folders']

    current_file_name = None

    file_types = {
        'photo': ['jpg', 'png'],
        'audio': ['mp3']
    }

    event_types = {
        'handled': 'handle',
        'error': 'error'
    }

    def __init__(self):
        """

        """
        self.disk_api = yadisk.YaDisk(self.yandex_app_key,
                                      self.yandex_app_secret,
                                      self.yandex_token)
        self.bot = telebot.TeleBot(self.telegram_bot_token)

        @self.bot.message_handler(commands=self.commands)
        def handle_commands(message):
            """

            :param message:
            :return:
            """
            self.log_event(event_type=self.event_types['handled'], event='command',
                           user_id=message.from_user.id, content=message.text)

            chat_id = message.chat.id

            self.command_handler(command=message.text, chat_id=chat_id)
            self.action_after_handling()

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message):
            """

            :param message:
            :return:
            """
            self.log_event(event_type=self.event_types['handled'], event='text',
                           user_id=message.from_user.id, content=message.text)

            chat_id = message.chat.id

            self.text_handler(text=message.text, chat_id=chat_id)

        @self.bot.message_handler(content_types=['audio'])
        def handle_audio(message):
            """

            :param message:
            :return:
            """
            self.log_event(event_type=self.event_types['handled'], event='audio',
                           user_id=message.from_user.id, content=message.text)

            self.audio_handler(audio=message.audio)
            self.action_after_handling()

        @self.bot.message_handler(content_types=['video'])
        def handle_video(message):
            """

            :param message:
            :return:
            """
            self.log_event(event_type=self.event_types['handled'], event='video',
                           user_id=message.from_user.id, content=message.text)

            self.video_handler(video=message.video)
            self.action_after_handling()

        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            """

            :param message:
            :return:
            """
            self.log_event(event_type=self.event_types['handled'], event='document',
                           user_id=message.from_user.id, content=message.text)

            self.document_handler(document=message.document)
            self.action_after_handling()

        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            """

            :param message:
            :return:
            """
            caption = message.caption
            self.log_event(event_type=self.event_types['handled'], event='photo',
                           user_id=message.from_user.id, content=caption)

            self.photo_handler(photo=message.photo, caption=caption)
            self.action_after_handling()

    def log_event(self, event_type=None, event=None, user_id=None, content=None):
        """

        :param event_type:
        :param event:
        :param user_id:
        :param content:
        :return:
        """

        assert event_type is not None
        assert event is not None
        assert user_id is not None

        if content is None:
            content = ''

        # time.localtime(tm_year=2018, tm_mon=3, tm_mday=25, tm_hour=23, tm_min=6, tm_sec=56, tm_wday=6, tm_yday=84,
        #                  tm_isdst=0)
        current_time = time.localtime()
        log_template = '{tm_hour}:{tm_min}:{tm_sec} {tm_mday}.{tm_mon}.{tm_year} ' \
                       '{event_type}: {event} from user: {user_id} content: {content} at {current_path}'

        log_string = log_template.format(tm_year=current_time[0], tm_mon=current_time[1],
                                         tm_mday=current_time[2], tm_hour=current_time[3],
                                         tm_min=current_time[4], tm_sec=current_time[5],
                                         event=event, event_type=event_type, user_id=user_id,
                                         content=content, current_path=self.current_path)
        print(log_string)

    def action_after_handling(self):
        self.current_file_name = None

    def get_obj(self, file_name=None, file_id=None):
        """

        :param file_name:
        :param file_id:
        :return:
        """

        assert file_name is not None
        assert file_id is not None

        file_info = self.bot.get_file(file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.
                            format(self.telegram_bot_token, file_info.file_path))

        with open(file_name, 'wb') as stream:
            stream.write(file.content)

    def command_handler(self, command=None, chat_id=None):
        """

        :param chat_id:
        :param command:
        :return:
        """

        assert command is not None

        command = command[1:]

        assert command in self.commands
        assert chat_id is not None

        self._handle_command(command, chat_id)

    def _handle_command(self, command, chat_id):
        """

        :param command:
        :param chat_id:
        :return:
        """

        assert command is not None
        assert chat_id is not None

        if command == 'start':
            self._command_start(chat_id=chat_id)
        if command == 'folders':
            self._command_folders(chat_id=chat_id)

    def _command_start(self, chat_id=None):
        """

        :param chat_id:
        :return:
        """

        assert chat_id is not None

        self.current_path = self.root_path

        folder_content = self._folder_content()
        markup = self._create_markup(folder_content)
        self.bot.send_message(chat_id=chat_id, text='hi! Now, you at {0} :'.format(self.current_path),
                              reply_markup=markup)

    def _command_folders(self, chat_id=None):
        """

        :param chat_id:
        :return:
        """
        assert chat_id is not None

        folder_content = self._folder_content()
        markup = self._create_markup(folder_content)
        self.bot.send_message(chat_id=chat_id, text='folders at {0} : '.format(self.current_path),
                              reply_markup=markup)

    def text_handler(self, text=None, chat_id=None):
        """

        :param chat_id:
        :param text:
        :return:
        """

        current_path = self.current_path + text + '/'
        if self.disk_api.is_file(current_path):
            file_type = self.file_type(current_path=current_path)
            content_type = None
            for type, extensions in self.file_types.items():
                if file_type in extensions:
                    content_type = type
                    break

            assert content_type is not None

            self._send_file_link(file_path=current_path, chat_id=chat_id,
                                 text=text, file_type=content_type)
        elif self.disk_api.is_dir(current_path):
            self.current_path = current_path
            self._command_folders(chat_id=chat_id)
        elif text == self.special_words['back']:
            try:
                self.current_path = self.current_path[:-1].split('/')
                self.current_path = self.current_path[:-1]

                path = self.current_path[0]
                for point in self.current_path[1:]:
                    path = path + '/' + point

                if path == 'disk:':
                    path = '{0}/'.format(path)

                self.current_path = path
                self._command_folders(chat_id=chat_id)

            except IndexError:
                self._update(chat_id=chat_id)
                self.log_event(event_type=self.event_types['error'], event='failed',
                               user_id=chat_id, content='nothing')

    def photo_handler(self, photo=None, caption=None):
        """

        :param caption:
        :param photo:
        :return:
        """

        assert photo is not None
        assert type(photo) == list
        assert len(photo) > 0

        # Get a photo with biggest size
        photo = photo[-1]

        photo_name = photo.file_id
        if caption is not None:
            photo_name = caption

        file_name = '{0}.{1}'.format(photo_name, self.file_types['photo'][0])
        self.get_obj(file_name=file_name, file_id=photo.file_id)
        self.disk_api.upload(path_or_file=file_name,
                             dst_path=self.current_path + file_name)
        os.remove(file_name)

    def video_handler(self, video=None):
        """

        :param video:
        :return:
        """
        pass

    def audio_handler(self, audio=None, caption=None):
        """

        :param caption:
        :param audio:
        :return:
        """

        track_name = audio.file_id
        if caption is not None:
            track_name = caption

        file_name = '{0}.{1}'.format(track_name, self.file_types['audio'][0])
        self.get_obj(file_name=file_name, file_id=audio.file_id)
        self.disk_api.upload(path_or_file=file_name,
                             dst_path=self.current_path + file_name)
        os.remove(file_name)

    def document_handler(self, document=None):
        """

        :param document:
        :return:
        """
        pass

    def file_type(self, current_path=None):
        """

        :param current_path:
        :return:
        """
        assert current_path is not None
        assert self.disk_api.is_file(current_path)

        return current_path.split('/')[-2].split('.')[1]

    def _send_file_link(self, file_path=None, chat_id=None, text=None, file_type=None):
        """

        :param file_path:
        :return:
        """

        assert file_path is not None
        assert text is not None
        assert file_type is not None

        file_link = self.disk_api.get_download_link(file_path)
        file_link_html = '<a href="{link}">{text}</a>'.format(link=file_link, text=text)

        if file_type == 'photo':
            self.bot.send_message(chat_id=chat_id, text=file_link_html,
                                  parse_mode="HTML")
        if file_type == 'audio':
            self.download(file_name=text, file_link=file_link)
            with open(text, 'rb') as audio:
                self.bot.send_audio(chat_id=chat_id, audio=audio, caption=text)
            os.remove(text)

    def download(self, file_name=None, file_link=None):
        """

        :param file_name:
        :param file_link:
        :return:
        """

        assert file_name is not None
        assert file_link is not None

        response = requests.get(file_link)
        with open(file_name, 'wb') as stream:
            stream.write(response.content)

    def _dirs_list(self):
        """

        :return:
        """
        folders = list()
        if self.disk_api.is_dir(self.current_path):
            folders = [folder.FIELDS['path'] for folder in self.disk_api.listdir(self.current_path)
                       if self.disk_api.is_dir(folder.FIELDS['path'])]

        return folders

    def _files_list(self):
        """

        :return:
        """
        files_list = list()
        if self.disk_api.is_dir(self.current_path):
            files_list = [folder.FIELDS['path'] for folder in self.disk_api.listdir(self.current_path)
                          if self.disk_api.is_file(folder.FIELDS['path'])]

        return files_list

    def _folder_content(self):
        """

        :return:
        """
        folder_content = list()
        if self.disk_api.is_dir(self.current_path):
            folder_content = [folder.FIELDS['path'].split('/')[-1] for folder in
                              self.disk_api.listdir(self.current_path)]

        return folder_content

    def _create_markup(self, items=None):
        """

        :param items:
        :return:
        """
        assert items is not None
        assert type(items) == list

        markup = types.ReplyKeyboardMarkup(row_width=1)
        buttons = [types.KeyboardButton(item) for item in items]

        markup.add(*buttons)
        if not self.current_path == self.root_path:
            markup.add(types.KeyboardButton(self.special_words['back']))

        return markup

    def _update(self, chat_id=None):
        """

        :param chat_id:
        :return:
        """

        assert chat_id is not None

        self._command_start(chat_id=chat_id)
