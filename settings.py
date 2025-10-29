import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

ip = os.getenv('IP_SERVER')
port = int(os.getenv('PORT_SERVER'))

BASE_DIR = Path(__file__).resolve().parent

# NOTE важные для приложения медиафайлы
images_folder = os.path.join(BASE_DIR, "APP/GUI/images")
# NOTE данные для работы софта
config_file = os.path.join(BASE_DIR, "APP/GUI/config_json.json")
# NOTE ВРЕМЕННЫЙ файл для хнарения новый аккаунтов для спама
accounts_file = os.path.join(BASE_DIR, "APP/GUI/account_data.json")
# NOTE рабочие медифайлы 
photos_folder = os.path.join(BASE_DIR, "photos")
# NOTE для сохранения файлов на каждый работающий аккаунт
account_folder = os.path.join(BASE_DIR, "accounts")
# NOTE для сохранения данных для настроек работы задач
settings_file = os.path.join(BASE_DIR, "APP/Settings/add_settings.json")
# NOTE для сохранения файлов с базами для рассылки
base_folder = os.path.join(BASE_DIR, "bases")
# NOTE для сохранения файлов отправленных через окно с общением в чатах (если мы или нам написали с медиафайлом)
user_media = os.path.join(BASE_DIR, "user_media")
# NOTE еще один путь до папки для архива с присылаемыми сообщениями, который по сути не нужен, но для начала нужно настроить сохранение сообщений даже из чатов и каналов.
# NOTE есть еще одна папка которая не используется которая раньше сохранаяла медиафайлы для рассылки.