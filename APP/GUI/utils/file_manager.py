import ast
import json
import os
import typing
import shutil

import chardet
from loguru import logger
from PyQt5 import QtGui, QtWidgets

from settings import photos_folder, config_file, images_folder, account_folder, accounts_file, settings_file, base_folder



class ConfigData:
    
    @classmethod
    def update(
        cls,
        key: str,
        value: str
        ) -> None:
        with open(config_file, "r", encoding="utf-8") as file:
            file_data: dict = json.loads(file.read())
            
        file_data[key] = value
            
        with open(config_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(file_data, ensure_ascii=False, indent=4))
    
    @classmethod
    def get(
        cls,
        key: str
        ) -> typing.Optional[typing.Any]:
        with open(config_file, "r", encoding="utf-8") as file:
            file_data: dict = json.loads(file.read())
        
        value = file_data.get(key)
            
        if value is not None:
            if "_file" in key:
                if os.path.exists(
                    os.path.join(photos_folder, file_data.get(key))
                    ):
                    return os.path.join(photos_folder, file_data.get(key))
                elif os.path.exists(
                    os.path.join(images_folder, file_data.get(key))
                    ):
                    return os.path.join(images_folder, file_data.get(key))
                else:
                    logger.warning("Файл не наеден")
                    return os.path.join(images_folder, file_data.get("default_file"))
                
            else:
                return value
            
        else:
            return
            # raise Exception("Data Not Found")

    @classmethod
    def get_all(
        cls
        ) -> dict:
        """
        Получаем все конфигурационные данные
        """
        with open(config_file,"r",encoding="utf-8") as file:
            return json.loads(file.read())

    @classmethod
    def choose_file(
        cls,
        MainWindow: QtWidgets.QMainWindow,
        media_label: QtWidgets.QLabel,
        config_key: str,
        file_: bool = False
        ):
        """
        Записывает файл в локальное хранилище;
        И обновляет переменную с путем для отображения в 
        приложении и использовании в работе аккаунта.
        """
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            MainWindow, 
            "Выбрать файл", 
            "", 
            # "All Files (*);;Text Files (*.txt);;Image Files (*.png *.jpg)", 
            "All Files (*)", 
            options=QtWidgets.QFileDialog.Options()
            )
        
        if file_name:        
            if config_key == "base_file":
                file_path = os.path.join(base_folder, os.path.basename(file_name)) #Используем os.path.basename для кроссплатформенности
            else:
                file_path = os.path.join(photos_folder, os.path.basename(file_name)) #Используем os.path.basename для кроссплатформенности
            logger.debug(f"Конечный файл: {file_path}")
            
            ConfigData.update(
                config_key,
                os.path.basename(file_name)
            )
                        
            try:
                with open(file_name, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding'] 
                    logger.debug(encoding)  # Пример: печатаем содержимое файла
                
                shutil.copy2(file_name, file_path) # Копируем файл
                logger.info(f"Файл скопирован в {file_path}")
                
                
                # Проверяем, является ли файл изображением
                try:                
                    if not file_:
                        media_label.setPixmap(QtGui.QPixmap(file_path))
                    else:
                        media_label.setPixmap(QtGui.QPixmap(ConfigData.get("yes_doc_file")))
                    media_label.setScaledContents(True)
                    media_label.setMaximumSize(100,100)
                        
                except Exception as e:
                    logger.error(f"Ошибка при попытке отобразить изображение: {e}")
                    media_label.clear() #Очищаем QLabel если файл не картинка
                                
            except Exception as e:
                logger.error(f"Ошибка открытия файла: {e}")


class AccountData:
    
    @classmethod
    def update(
        cls,
        key: str,
        value: str
        ) -> None:
        with open(accounts_file, "r", encoding="utf-8") as file:
            file_data: dict = json.loads(file.read())
            
        file_data[key] = value
            
        with open(accounts_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(file_data, ensure_ascii=False, indent=4))
    
    @classmethod
    def get(
        cls,
        key: str,
        _file: typing.Optional[bool] = None
        ) -> typing.Any:
        with open(accounts_file, "r", encoding="utf-8") as file:
            account_data: dict = json.loads(file.read())
        
        if _file:
            with open(config_file, "r", encoding="utf-8") as file:
                config_data: dict = json.loads(file.read())
            
            logger.debug(os.path.join(account_folder, str(account_data.get(key))))
            
            if os.path.exists(
                os.path.join(account_folder, str(account_data.get(key)))
                ):
                return os.path.join(images_folder, config_data.get("yes_doc_file"))
            else:
                logger.warning("Файл не наеден")
                return os.path.join(images_folder, config_data.get("no_doc_file"))
        else:
            return account_data.get(key,"")

    @classmethod
    def choose_file(
        cls,
        parent: QtWidgets.QWidget,
        media_label: QtWidgets.QLabel,
        key: str,
        filter: str = "Files (*)"
        ):
        """
        Добавляем сессию.
        """
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent, 
            "Выбрать аккаунт в формате .session или архив tdata", 
            "", 
            filter, 
            options=QtWidgets.QFileDialog.Options()
            )
        
        if file_name:
            file_path = os.path.join(account_folder, os.path.basename(file_name)) #Используем os.path.basename для кроссплатформенности

            logger.debug(f"Конечный файл: {file_path}")
            
            cls.update(
                key,
                os.path.basename(file_name)
            )
            
            try:
                shutil.copy2(file_name, file_path) # Копируем файл
                logger.info(f"Файл скопирован в {file_path}")
                
                media_label.setPixmap(QtGui.QPixmap(ConfigData.get("yes_doc_file")))
                media_label.setScaledContents(True)
                media_label.setMaximumSize(100,100)
                
            except Exception as e:
                logger.error(f"Ошибка открытия файла: {e}")


class SettingsData:
    
    @classmethod
    def str_to_python_obj(
        cls,
        value: str
        ) -> typing.Any:
        """
        Из строки в: strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
        """
        try:
            return ast.literal_eval(value)
        except SyntaxError:
            return value
    
    @classmethod
    def update(
        cls,
        list_keys: list[str],
        value: str
        ) -> None:
        with open(settings_file, "r", encoding="utf-8") as file:
            file_data: dict = json.loads(file.read())
            
        logger.debug(list_keys)
            
        if len(list_keys) == 1:
            file_data[list_keys[0]] = cls.str_to_python_obj(value)
        elif len(list_keys) == 2:
            file_data[list_keys[0]][list_keys[1]] = cls.str_to_python_obj(value)
        elif len(list_keys) == 3:
            file_data[list_keys[0]][list_keys[1]][list_keys[2]] = cls.str_to_python_obj(value)
        else:
            raise Exception(f"Длина списка == {len(list_keys)}\nЧто не поддерживается данным приложением.")
            
        with open(settings_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(file_data, ensure_ascii=False, indent=4))
    
    @classmethod
    def get(
        cls,
        list_keys: list[str]
        ) -> typing.Any:
        setting: dict = cls.get_all()
        for key in list_keys:
            setting = setting[key]
        else:
            logger.debug(setting)
            return setting

    @classmethod
    def get_all(
        cls
        ) -> dict:
        with open(settings_file, "r", encoding="utf-8") as file:
            return json.loads(file.read())

