import os
import base64
import datetime
import typing
import json

from PyQt5 import QtCore, QtWebSockets, QtWidgets
from PyQt5.QtCore import QUrl
from loguru import logger

from APP.GUI.main import Ui_MainWindow
from APP.GUI.utils.custom_widgets import ErrorAlert, ResultRequestAlert
from settings import photos_folder, account_folder, base_folder, user_media


class WebSocketClient(QtCore.QObject):
    """
    Создаем разные объекты сигналов
    для работы с разными виджетами
        
        {
            "type": 'progress', 'account'
            "data": ...
        }
        
    """
    progress_received = QtCore.pyqtSignal(list)
    account_received = QtCore.pyqtSignal(list)
    push_received = QtCore.pyqtSignal(dict)
    
    connection_closed = QtCore.pyqtSignal()
    connection_error = QtCore.pyqtSignal(str)

    chats_account = QtCore.pyqtSignal(list)
    chat_messages = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        # self.socket.errorOccurred.connect(self.on_error)
        self.socket.textMessageReceived.connect(self.on_message)
        self.url = None
        self._connected = False
        self.user_id = False
        # self.processed_messages: list = []  # Храним здесь ID обработанных сообщений
        
    def connect(self, url):
        self.url = QUrl(url)
        self.socket.open(self.url)
        self._connected = True
        logger.info("Успешное подключение к WebSocket-серверу.")

    def on_connected(self):
        logger.success("WebSocket connected")

    def on_disconnected(self):
        logger.error("WebSocket disconnected")
        self.connection_closed.emit()

    def disconnect(self):
        # Логика отключения
        self._connected = False

    def is_connected(self):
        return self._connected

    # def on_error(self, error):
    #     logger.warning(f"WebSocket error: {error}")
    #     self.connection_error.emit(str(error))

    # def add_uniq_id(self, data: dict) -> dict:
    #     uniq_id = random.randint(100000,999999)
    #     self.processed_messages.append(uniq_id)
    #     data['uniq_id'] = uniq_id
    #     return data

    # def check_uniq_id(
    #     self, 
    #     data: dict
    #     ) -> typing.Optional[bool]:
    #     try:
    #         if data.get("uniq_id") in self.processed_messages:
    #             self.processed_messages.remove(
    #                 data.get("uniq_id")
    #                 )
    #             return True
    #     except:
    #         pass
        
    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def send_data(self, data: dict):
        """
        Отправляет данные на сервер в формате JSON.
        """
        try:
            # data = self.add_uniq_id(data)
            json_data = json.dumps(data, default=self.json_serial)
            self.socket.sendTextMessage(json_data)  # Имитируем получение для обработки
        except Exception as e:
            logger.error(f"Ошибка при отправке данных: {e}") # Ошибка при отправке данных: Type <class 'bytes'> not serializable
        
    def on_message(self, message):
        """
        Получает все данные по вебсокету.
        """
        try:
            data: dict = json.loads(message)
            logger.debug(data)
            # if not self.check_uniq_id(data.get("data")): return
            if data.get("type") == 'all_accounts':
                """
                Для обновления данных обо всех акках.
                """
                self.account_received.emit(data.get("data"))
            elif data.get("type") == 'push':
                """
                Для вызова пуша.
                """
                self.push_received.emit(data.get("data"))
            elif data.get("type") == 'all_progress':
                """
                Для обновления прогресса.
                """
                self.progress_received.emit(data.get("data"))
            elif data.get("type") == 'chats_account':
                """
                Для обновления чатов аккаунта.
                """
                self.chats_account.emit(data.get("data"))
            elif data.get("type") == 'chat_messages':
                """
                Для обновления истории общения.
                """
                self.chat_messages.emit(data.get("data"))
            elif data.get("type") == 'user_id':
                """
                Для записи уникального идентификатора.
                """
                user_data = data.get("data")
                self.user_id = user_data['user_id']
                logger.success(f"Установлен новый идентификатор пользователя: {self.user_id}")
            # elif data.get("type") == 'progress':
            #     """
            #     Для изменения данных о прогрессе.
            #     """
            #     self.progress_received.emit(data.get("data"))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")


class WebSocketApplication(QtWidgets.QMainWindow):
    
    def __init__(self, application, ip: str, port: int):
        super().__init__()
        self.application: Ui_MainWindow = application
        self.ip = ip
        self.port = port

        self.websocket_client = WebSocketClient()
        self.websocket_client.progress_received.connect(self.update_progress)
        self.websocket_client.account_received.connect(self.update_account)
        self.websocket_client.push_received.connect(self.push_in_app)
        self.websocket_client.connection_closed.connect(self.on_websocket_closed)
        self.websocket_client.connection_error.connect(self.on_websocket_error)
        self.websocket_client.chats_account.connect(self.update_chats_account)
        self.websocket_client.chat_messages.connect(self.update_chat_messages)
        
        # Таймер для повторного подключения
        self.reconnect_timer = QtCore.QTimer()
        self.reconnect_timer.timeout.connect(self.reconnect_to_server)
        self.reconnect_interval = 3000  # Интервал повторного подключения (1 секунд(у,ы))

        # Подключаемся к серверу
        self.connect_to_server()
                
        self.application.tab_all_accs.button_add_account.connect(
            self.send_new_account_to_server
            )
        self.application.tab_all_accs.button_delete_account.connect(
            self.send_delete_account_to_server
            )
        self.application.tab.start_btn.button_new_task.connect(
            self.send_new_task_to_server
            )
        self.application.chat_page.account_list_widget.account_selected.connect(
            self.get_chats_account
            )
        self.application.chat_page.chat_list_widget.chat_selected.connect(
            self.get_chat_history
            )
        self.application.chat_page.chat_widget.message_sent.connect(
            self.send_msg_in_chat
            )
        
    def connect_to_server(self):
        """
        Подключаемся к WebSocket-серверу.
        """
        try:
            self.websocket_client.connect(f"ws://{self.ip}:{self.port}/ws")
            self.reconnect_timer.stop()  # Останавливаем таймер после успешного подключения
        except Exception as e:
            logger.error(f"Ошибка подключения к WebSocket-серверу: {e}")
            self.reconnect_timer.start(self.reconnect_interval)  # Запускаем таймер для повторного подключения

    def reconnect_to_server(self):
        """
        Попытка повторного подключения к серверу.
        """
        if self.websocket_client.is_connected():  # Проверяем, не подключены ли мы уже
            logger.info("Уже подключены к серверу. Останавливаем таймер.")
            self.reconnect_timer.stop()
            return

        logger.info("Попытка повторного подключения к серверу...")
        self.connect_to_server()

    def on_websocket_closed(self):
        """
        Обработка события разрыва соединения.
        """
        logger.warning("Соединение с WebSocket-сервером разорвано.")
        self.websocket_client.disconnect()  # Сбрасываем состояние соединения
        self.reconnect_timer.start(self.reconnect_interval)  # Запускаем таймер для повторного подключения

    def on_websocket_error(self, error):
        """
        Обработка ошибки соединения.
        """
        logger.error(f"Ошибка WebSocket: {error}")
        self.websocket_client.disconnect()  # Сбрасываем состояние соединения
        self.reconnect_timer.start(self.reconnect_interval)  # Запускаем таймер для повторного подключения

    def update_progress(self, data):
        """
        Обновляем данные с прогрессом.
        """
        logger.info(data)
        self.application.tab_progress.create_all_progress_blocks(data)

    def push_in_app(self, result: dict):
        """
        Уведомляем о результате отправленных данных.
        """
        logger.info(result)
        
        if result.get("status") == "success":
            ResultRequestAlert().show_message(
                result['title'],
                result['message'],
                parent=self
            )
        else:
            ErrorAlert().show_message(
                result['title'],
                result['message']
            )

    def update_account(self, data: list[dict]):
        """
        Обновляем данные для аккаунта.
        """
        self.application.tab_all_accs.create_now_accounts_form(data)
        self.application.tab.account_choice_form.add_content_accs(data)
        self.application.chat_page.account_list_widget.add_accounts(data)

    def update_chats_account(self, data: list[dict]):
        """
        Обновляем данные чатов аккаунта.
        """
        self.application.chat_page.chat_list_widget.create_chat_list(data)

    def get_chats_account(self, account_phone: str):
        """
        Отправляет запрос на обновление чатов аккаунта.
        """
        logger.success("get_chats_account")
        data = {
            "type": "get_chats_account",
            "user_id": self.websocket_client.user_id,
            "data": account_phone,
            }
        self.websocket_client.send_data(data)
    
    def update_chat_messages(self, data: list[dict]):
        """
        Обновляем данные переписки.
        """
        self.application.chat_page.chat_widget.create_chat_history(data)

    def get_chat_history(self, chat_selected_data: dict):
        """
        Отправляет запрос на обновление чатов аккаунта.
        """
        logger.success("get_chat_history")
        data = {
            "type": "get_chat_history",
            "user_id": self.websocket_client.user_id,
            "data": chat_selected_data,
            }
        self.websocket_client.send_data(data)
    
    def send_msg_in_chat(self, new_msg_data: dict):
        """
        Отправляет запрос на отправку сообщения в чат.
        """
        logger.success("send_msg_in_chat")
        msg_data = self.convert_file_data(new_msg_data, message=True)
        data = {
            "type": "send_msg_in_chat",
            "user_id": self.websocket_client.user_id,
            "data": msg_data,
            }
        self.websocket_client.send_data(data)
    
    def send_new_task_to_server(self, task_data: dict):
        """
        Отправляет данные на сервер для запуска задачи.
        """
        logger.success("new_task")
        task_data = self.convert_file_data(task_data, task=True)
        data = {
            "type": "new_task",
            "user_id": self.websocket_client.user_id,
            "data": task_data,
            }
        self.websocket_client.send_data(data)
    
    def send_new_account_to_server(self, account_data: dict):
        """
        Отправляет данные на сервер для добавления аккаунта.
        """
        logger.success("new_account")
        account_data = self.convert_file_data(account_data, account=True)
        data = {
            "type": "new_account",
            "user_id": self.websocket_client.user_id,
            "data": account_data,
            }
        self.websocket_client.send_data(data)
    
    def send_delete_account_to_server(self, material_id: int):
        """
        Отправляет данные на сервер для удаления аккаунта.
        """
        logger.success("delete_account")
        data = {
            "type": "delete_account",
            "user_id": self.websocket_client.user_id,
            "material_id": material_id,
            }
        self.websocket_client.send_data(data)
    
    def convert_file_data(
        self, 
        config_data: dict,
        *,
        account: typing.Optional[bool] = None,
        task: typing.Optional[bool] = None,
        message: typing.Optional[bool] = None
        ) -> dict:
        """
        Находим все пути к файлам которые могут быть в нашем словарике
        после чего при наличии добавляем в словарик files открытыми
        а в самом словарике заменяем значение на ключ из словаря files
        
        Находим:
            ['message_data']['media']
            ['base_file']
            ['answer_data']['media']
            
            ['session_path']
            ['account_photo']

            ['file_path']
        """
        def save_bytes_file(
            folder: str,
            config_data: dict, 
            key: str,
            *,
            delete: typing.Optional[bool] = None
            ) -> dict:
            file_path = config_data[key]
            if file_path:
                file_path = os.path.join(folder, file_path)
                
                if file_path and os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    with open(file_path, 'rb') as file:
                        config_data[key] = {file_name: base64.b64encode(file.read()).decode('utf-8')}
                else:
                    config_data[key] = None
                    
                if delete and os.path.exists(file_path):
                    os.remove(file_path)
                
            return config_data
        
        if task:
            config_data = save_bytes_file(base_folder, config_data, 'base_file')
                        
            send_file = config_data['message_data']['media']
            file_path = os.path.join(photos_folder, send_file)
            
            if send_file and os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                with open(file_path, 'rb') as file:
                    config_data['message_data']['media'] = {file_name: base64.b64encode(file.read()).decode('utf-8')}
            else:
                config_data['message_data']['media'] = None
                
            # if os.path.exists(file_path):
            #     os.remove(file_path)
            
            try:
                answer_file = config_data['answer_data']['media']
                file_path = os.path.join(photos_folder, answer_file)
                
                if answer_file and os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    with open(file_path, 'rb') as file:
                        config_data['answer_data']['media'] = {file_name: base64.b64encode(file.read()).decode('utf-8')}
                else:
                    config_data['answer_data']['media'] = None
            except:
                config_data['answer_data']['media'] = None
            
            # if os.path.exists(file_path):
            #     os.remove(file_path)
            
        elif account:
            config_data = save_bytes_file(account_folder, config_data, 'session_path')
            config_data = save_bytes_file(account_folder, config_data, 'account_photo', delete=True)
        elif message:
            config_data = save_bytes_file(user_media, config_data, 'file_path', delete=True)
                            
        return config_data

