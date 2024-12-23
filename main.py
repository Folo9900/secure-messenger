from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
import requests
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Базовый URL API
API_URL = os.getenv('API_URL', 'http://localhost:5000')

# Определение UI в Kivy Language
KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        md_bg_color: get_color_from_hex("#0E1621")

        Widget:
            size_hint_y: 0.2

        MDLabel:
            text: "Secure Messenger"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#FFFFFF")
            size_hint_y: None
            height: dp(50)

        MDTextField:
            id: username
            hint_text: "Имя пользователя"
            mode: "rectangle"
            helper_text_mode: "on_error"

        MDTextField:
            id: password
            hint_text: "Пароль"
            mode: "rectangle"
            password: True
            helper_text_mode: "on_error"

        MDRaisedButton:
            text: "Войти"
            size_hint_x: 0.8
            pos_hint: {"center_x": .5}
            md_bg_color: get_color_from_hex("#2B5278")
            on_release: root.login()

        MDRaisedButton:
            text: "Регистрация"
            size_hint_x: 0.8
            pos_hint: {"center_x": .5}
            md_bg_color: get_color_from_hex("#17212B")
            on_release: root.register()

        Widget:
            size_hint_y: 0.3

<ChatScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: get_color_from_hex("#0E1621")

        MDTopAppBar:
            title: "Чаты"
            right_action_items: [["logout", lambda x: root.logout()]]
            md_bg_color: get_color_from_hex("#17212B")

        MDBoxLayout:
            orientation: 'horizontal'
            
            # Список контактов
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.3
                md_bg_color: get_color_from_hex("#17212B")
                
                MDScrollView:
                    MDList:
                        id: contacts_list

            # Область чата
            MDBoxLayout:
                orientation: 'vertical'
                
                MDScrollView:
                    id: chat_scroll
                    MDList:
                        id: chat_messages
                        spacing: dp(10)
                        padding: dp(10)

                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(60)
                    padding: dp(10)
                    spacing: dp(10)
                    md_bg_color: get_color_from_hex("#17212B")

                    MDTextField:
                        id: message_input
                        hint_text: "Сообщение"
                        mode: "rectangle"
                        multiline: False
                        size_hint_x: 0.8

                    MDIconButton:
                        icon: "send"
                        theme_text_color: "Custom"
                        text_color: get_color_from_hex("#2B5278")
                        on_release: root.send_message()
'''

class LoginScreen(MDScreen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        
        try:
            response = requests.post(f"{API_URL}/login", json={
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                app = MDApp.get_running_app()
                app.token = data['token']
                app.current_user_id = data['user_id']
                app.switch_screen('chat')
            else:
                self.ids.password.error = True
                self.ids.password.helper_text = "Неверные учетные данные"
        except Exception as e:
            self.ids.password.error = True
            self.ids.password.helper_text = "Ошибка подключения к серверу"

    def register(self):
        username = self.ids.username.text
        password = self.ids.password.text
        
        try:
            response = requests.post(f"{API_URL}/register", json={
                'username': username,
                'password': password
            })
            
            if response.status_code == 201:
                self.login()
            else:
                self.ids.username.error = True
                self.ids.username.helper_text = "Пользователь уже существует"
        except Exception as e:
            self.ids.username.error = True
            self.ids.username.helper_text = "Ошибка подключения к серверу"

class ChatScreen(MDScreen):
    current_chat_user = None
    
    def on_enter(self):
        self.load_contacts()
        Clock.schedule_interval(self.update_messages, 5)  # Обновление каждые 5 секунд

    def load_contacts(self):
        app = MDApp.get_running_app()
        headers = {'Authorization': f'Bearer {app.token}'}
        
        try:
            response = requests.get(f"{API_URL}/users", headers=headers)
            if response.status_code == 200:
                contacts = response.json()
                self.ids.contacts_list.clear_widgets()
                for contact in contacts:
                    item = TwoLineListItem(
                        text=contact['username'],
                        secondary_text="",
                        on_release=lambda x, user_id=contact['id']: self.select_chat(user_id)
                    )
                    self.ids.contacts_list.add_widget(item)
        except Exception as e:
            print("Ошибка загрузки контактов:", e)

    def select_chat(self, user_id):
        self.current_chat_user = user_id
        self.load_messages()

    def load_messages(self):
        if not self.current_chat_user:
            return
            
        app = MDApp.get_running_app()
        headers = {'Authorization': f'Bearer {app.token}'}
        
        try:
            response = requests.get(
                f"{API_URL}/messages/{self.current_chat_user}",
                headers=headers
            )
            if response.status_code == 200:
                messages = response.json()
                self.ids.chat_messages.clear_widgets()
                for message in messages:
                    is_own = message['sender_id'] == app.current_user_id
                    message_card = MDCard(
                        orientation='vertical',
                        size_hint_y=None,
                        height=dp(60),
                        padding=dp(10),
                        pos_hint={'right': 1} if is_own else {'x': 0},
                        size_hint_x=0.7,
                        md_bg_color=get_color_from_hex("#2B5278") if is_own else get_color_from_hex("#17212B")
                    )
                    message_card.add_widget(MDLabel(
                        text=message['content'],
                        theme_text_color="Custom",
                        text_color=get_color_from_hex("#FFFFFF")
                    ))
                    self.ids.chat_messages.add_widget(message_card)
                
                # Прокрутка к последнему сообщению
                self.ids.chat_scroll.scroll_y = 0
        except Exception as e:
            print("Ошибка загрузки сообщений:", e)

    def send_message(self):
        if not self.current_chat_user:
            return
            
        message_text = self.ids.message_input.text.strip()
        if not message_text:
            return
            
        app = MDApp.get_running_app()
        headers = {'Authorization': f'Bearer {app.token}'}
        
        try:
            response = requests.post(
                f"{API_URL}/messages",
                headers=headers,
                json={
                    'receiver_id': self.current_chat_user,
                    'content': message_text
                }
            )
            if response.status_code == 201:
                self.ids.message_input.text = ""
                self.load_messages()
        except Exception as e:
            print("Ошибка отправки сообщения:", e)

    def update_messages(self, dt):
        if self.current_chat_user:
            self.load_messages()

    def logout(self):
        app = MDApp.get_running_app()
        app.token = None
        app.current_user_id = None
        app.switch_screen('login')

class MessengerApp(MDApp):
    token = None
    current_user_id = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        # Создаем менеджер экранов
        self.sm = MDScreenManager()
        
        # Добавляем экраны
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(ChatScreen(name='chat'))
        
        return self.sm

    def switch_screen(self, screen_name):
        self.sm.current = screen_name

if __name__ == '__main__':
    MessengerApp().run()
