import asyncio
import json
import os
import typing
import concurrent.futures

from loguru import logger
from PyQt5 import QtCore, QtGui, QtWidgets

from APP.GUI.utils.order import StartWork
from APP.GUI.utils.file_manager import *
from settings import photos_folder
from APP.GUI.utils.custom_widgets import *



def run_in_thread(func, *args, **kwargs):
    """Запускает асинхронную функцию в отдельном потоке и ожидает результат."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, func(*args, **kwargs)) # Запускаем asyncio.run внутри потока
        return future.result()

# def run_in_thread(func):
#     """Декоратор для запуска функции в отдельном потоке."""
#     def wrapper(*args, **kwargs):
#         loop = asyncio.get_running_loop() # Получаем текущий event loop
#         with concurrent.futures.ThreadPoolExecutor() as pool: # Создаем пул потоков
#             return loop.run_in_executor(pool, func, *args, **kwargs) # Запускаем функцию в потоке
#     return wrapper


class AccountWidget(QtWidgets.QWidget):
    
    def __init__(self, account_data: dict):
        super().__init__()
        self.account_data = account_data
        self.is_expanded = False
        
        self.expand_icon = QtGui.QPixmap(
            os.path.join(images_folder, "down_small_arrow_icon.png")
            ).scaled(16, 16)
        self.minimise_icon = QtGui.QPixmap(
            os.path.join(images_folder, "up_small_arrow_icon.png")
            ).scaled(16, 16)

        self.icon1_label = QtWidgets.QLabel()
        self.icon2_label = QtWidgets.QLabel(
            account_data['name']
        )
        self.expand_button = QtWidgets.QPushButton()
        # Установка иконки на кнопку
        self.expand_button.setIcon(
            QtGui.QIcon(
                self.expand_icon
                )
            )
        self.expand_button.setIconSize(QtCore.QSize(16, 16)) # Установка размера иконки (важно!)

        # Загрузка иконок
        self.black_circle = WidgetTools.create_circle_pixmap(
            16, 
            QtGui.QColor("black")
            )
        self.green_circle = WidgetTools.create_circle_pixmap(
            16, 
            QtGui.QColor("green")
            )

        self.icon1_label.setPixmap(self.black_circle)

        self.details_layout = QtWidgets.QVBoxLayout() # Для динамически добавляемых деталей
        self.details_widget = QtWidgets.QWidget() # Виджет-контейнер для деталей
        self.details_widget.setLayout(self.details_layout)
        self.details_widget.setVisible(False) # Скрываем изначально

        main_layout = QtWidgets.QVBoxLayout(self)

        header_layout = QtWidgets.QHBoxLayout() # Шапка аккаунта
        header_layout.addWidget(self.icon1_label)
        header_layout.addWidget(self.icon2_label)
        header_layout.addWidget(self.expand_button)
        main_layout.addLayout(header_layout)

        main_layout.addWidget(self.details_widget) # Добавляем контейнер для деталей

        self.expand_button.clicked.connect(self.toggle_details)

    def toggle_details(self):
        self.is_expanded = not self.is_expanded
        self.details_widget.setVisible(self.is_expanded)
        self.expand_button.setIcon(
            QtGui.QIcon(
                self.minimise_icon if self.is_expanded else self.expand_icon
                )
            )
        if self.is_expanded:
            self.add_details()
        else:
            self.clear_details()

    def add_details(self):
        for key, value in self.account_data.items():
            label = QtWidgets.QLabel(f"{key}: {value}")
            self.details_layout.addWidget(label)

    def clear_details(self):
        for i in reversed(range(self.details_layout.count())): # Удаляем виджеты с конца, чтобы избежать ошибок индексации
            widget = self.details_layout.itemAt(i).widget()
            widget.setParent(None) # Важно отвязать виджет от родителя перед удалением

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            list_accounts: typing.Optional[list] = ConfigData.get("list_accounts")
            if list_accounts is None:
                list_accounts = []
            
            if WidgetTools.pixmap_equal(self.icon1_label.pixmap(), self.black_circle):
                self.icon1_label.setPixmap(self.green_circle)
                list_accounts.append(self.account_data['phone'])
            else:
                self.icon1_label.setPixmap(self.black_circle)
                try:
                    list_accounts.remove(self.account_data['phone'])
                except ValueError:
                    logger.warning("Нечего было удалять")
                    
            ConfigData.update("list_accounts",list_accounts)
                
        super().mousePressEvent(event)


class OrderPage(QtWidgets.QWidget):
    
    def __init__(self, MainWindow, _translate):
        super().__init__()
        
        ConfigData.update("list_accounts",[])

        self.setObjectName("tab")
        self.verticalLayout_25 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_25.setObjectName("verticalLayout_25")
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.verticalLayout_right = QtWidgets.QVBoxLayout()
        self.verticalLayout_right.setObjectName("verticalLayout_right")
        self.label_15 = QtWidgets.QLabel(self)
        self.label_15.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.verticalLayout_right.addWidget(self.label_15)
        
        # Чекбоксы с вариантом таргета
        self.variation_target_form = QtWidgets.QVBoxLayout()
        self.variation_target_form.setObjectName("variation_target_form")
        
        self.target_group = QtWidgets.QButtonGroup(self)  # Создаем группу для целевого варианта
        self.target_group.setObjectName("target_group")
        
        self.variation_target_user = QtWidgets.QRadioButton(self)
        self.variation_target_user.setObjectName("variation_target_user")
        self.target_group.addButton(self.variation_target_user)  # Добавляем в группу
        
        self.variation_target_user.setChecked(
            "user" == ConfigData.get("variation_target")
        )
        self.variation_target_user.clicked.connect(
            lambda x: ConfigData.update("variation_target","user")
        )
        
        self.variation_target_form.addWidget(self.variation_target_user)
        
        self.variation_target_chat = QtWidgets.QRadioButton(self)
        self.variation_target_chat.setObjectName("variation_target_chat")
        self.target_group.addButton(self.variation_target_chat)  # Добавляем в группу

        self.variation_target_chat.setChecked(
            "chat" == ConfigData.get("variation_target")
        )
        self.variation_target_chat.clicked.connect(
            lambda x: ConfigData.update("variation_target","chat")
        )
        
        self.variation_target_form.addWidget(self.variation_target_chat)
        
        self.verticalLayout_right.addLayout(self.variation_target_form)
        
        # Чекбоксы с вариантом базы
        self.variation_base_form = QtWidgets.QVBoxLayout()
        self.variation_base_form.setObjectName("variation_base_form")
        
        self.base_group = QtWidgets.QButtonGroup(self)  # Создаем группу для базового варианта
        self.base_group.setObjectName("base_group")
        
        self.variation_base_user = QtWidgets.QRadioButton(self)
        self.variation_base_user.setObjectName("variation_base_user")
        self.base_group.addButton(self.variation_base_user)  # Добавляем в группу
        
        self.variation_base_user.setChecked(
            "user" == ConfigData.get("variation_base")
        )
        self.variation_base_user.clicked.connect(
            lambda x: ConfigData.update("variation_base","user")
        )
        
        self.variation_base_form.addWidget(self.variation_base_user)
        
        self.variation_base_chat = QtWidgets.QRadioButton(self)
        self.variation_base_chat.setObjectName("variation_base_chat")
        self.base_group.addButton(self.variation_base_chat)  # Добавляем в группу
        
        self.variation_base_chat.setChecked(
            "chat" == ConfigData.get("variation_base")
        )
        self.variation_base_chat.clicked.connect(
            lambda x: ConfigData.update("variation_base","chat")
        )
        
        self.variation_base_form.addWidget(self.variation_base_chat)
        
        self.verticalLayout_right.addLayout(self.variation_base_form)
        
        self.use_have_base = QtWidgets.QCheckBox(self)
        self.use_have_base.setObjectName("use_have_base")
        
        self.use_have_base.setChecked(
            ConfigData.get("use_have_base")
        )
        self.use_have_base.clicked.connect(
            lambda x: ConfigData.update(
                "use_have_base",
                self.use_have_base.isChecked()
                )
        )
        
        self.verticalLayout_right.addWidget(self.use_have_base)
        self.target_base_file = QtWidgets.QLabel(self)
        self.target_base_file.setText("")
        self.target_base_file.setObjectName("target_base_file")
        self.target_base_file.setPixmap(
            QtGui.QPixmap(
                ConfigData.get("yes_doc_file") if ConfigData.get("base_file") else ConfigData.get("no_doc_file")
                )
            )
        self.target_base_file.setScaledContents(True)
        self.target_base_file.setMaximumSize(100,100)

        self.verticalLayout_right.addWidget(self.target_base_file)
        self.pushButton_5 = QtWidgets.QPushButton(self)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.clicked.connect(
            lambda x: ConfigData.choose_file(MainWindow, self.target_base_file, "base_file")
            )
        self.verticalLayout_right.addWidget(self.pushButton_5)
        self.settings_other = QtWidgets.QVBoxLayout()
        self.settings_other.setObjectName("settings_other")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_22 = QtWidgets.QLabel(self)
        self.label_22.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName("label_22")
        self.verticalLayout_14.addWidget(self.label_22)
        self.uniq_profile = QtWidgets.QCheckBox(self)
        self.uniq_profile.setObjectName("uniq_profile")
        
        self.uniq_profile.setChecked(
            ConfigData.get("uniq_profile")
        )
        self.uniq_profile.clicked.connect(
            lambda x: ConfigData.update(
                "uniq_profile",
                self.uniq_profile.isChecked()
                )
        )
        
        self.verticalLayout_14.addWidget(self.uniq_profile)
        self.slow_mode = QtWidgets.QCheckBox(self)
        self.slow_mode.setObjectName("slow_mode")
        
        self.slow_mode.setChecked(
            ConfigData.get("slow_mode")
        )
        self.slow_mode.clicked.connect(
            lambda x: ConfigData.update(
                "slow_mode",
                self.slow_mode.isChecked()
                )
        )
        
        self.verticalLayout_14.addWidget(self.slow_mode)
        self.translate_fio = QtWidgets.QCheckBox(self)
        self.translate_fio.setObjectName("translate_fio")
        
        self.translate_fio.setChecked(
            ConfigData.get("translate_fio")
        )
        self.translate_fio.clicked.connect(
            lambda x: ConfigData.update(
                "translate_fio",
                self.translate_fio.isChecked()
                )
        )
        
        self.verticalLayout_14.addWidget(self.translate_fio)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_23 = QtWidgets.QLabel(self)
        self.label_23.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")
        self.verticalLayout_3.addWidget(self.label_23)
        self.start_now = QtWidgets.QCheckBox(self)
        self.start_now.setObjectName("start_now")
        
        self.start_now.setChecked(
            ConfigData.get("start_now")
        )
        self.start_now.clicked.connect(
            lambda x: ConfigData.update(
                "start_now",
                self.start_now.isChecked()
                )
        )
        
        self.verticalLayout_3.addWidget(self.start_now)
        self.dateTimeEdit_5 = QtWidgets.QDateTimeEdit(self)
        self.dateTimeEdit_5.setObjectName("dateTimeEdit_5")
        self.verticalLayout_3.addWidget(self.dateTimeEdit_5)
        self.verticalLayout_14.addLayout(self.verticalLayout_3)
        self.settings_other.addLayout(self.verticalLayout_14)
        self.verticalLayout_right.addLayout(self.settings_other)
        self.gridLayout_8.addLayout(self.verticalLayout_right, 0, 2, 1, 1)
                            
        # NOTE тут добавляем объект
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self.account_choice_form = self.AccountList()
        scroll_area.setWidget(self.account_choice_form)

        self.gridLayout_8.addWidget(scroll_area, 0, 0, 1, 1)
        # END
        self.account_data_form = QtWidgets.QVBoxLayout()
        self.account_data_form.setObjectName("account_data_form")
        self.variation_work_title = QtWidgets.QLabel(self)
        self.variation_work_title.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.variation_work_title.setAlignment(QtCore.Qt.AlignCenter)
        self.variation_work_title.setObjectName("variation_work_title")
        self.account_data_form.addWidget(self.variation_work_title)
        self.tabWidget_3 = QtWidgets.QTabWidget(self)
        self.tabWidget_3.setMinimumSize(QtCore.QSize(0, 332))
        self.tabWidget_3.setObjectName("tabWidget_3")
        
        self.tab_static = QtWidgets.QWidget()
        self.tab_static.setObjectName("tab_static")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.tab_static)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.static_work = QtWidgets.QToolBox(self.tab_static)
        self.static_work.setMinimumSize(QtCore.QSize(500, 277))
        self.static_work.setMinimumWidth(600)  # Увеличена минимальная ширина
        self.static_work.setObjectName("static_work")

        self.static_text_form = QtWidgets.QWidget()
        self.static_text_form.setObjectName("static_text_form")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.static_text_form)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        
        self.static_text_content = MyTextEdit("static_text_content", self.static_text_form)
        
        self.horizontalLayout_9.addWidget(self.static_text_content)

        self.static_media_form = QtWidgets.QWidget()
        self.static_media_form.setObjectName("static_media_form")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.static_media_form)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.media_file = QtWidgets.QLabel(self.static_media_form)
        self.media_file.setText("")
        self.media_file.setObjectName("media_file")
        self.media_file.setPixmap(QtGui.QPixmap(ConfigData.get("mailing_media_file")))
        self.media_file.setScaledContents(True)
        self.media_file.setMaximumSize(100,100)
        self.verticalLayout_5.setAlignment(QtCore.Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.media_file)

        self.static_work.addItem(self.static_text_form, "")
        self.static_work.addItem(self.static_media_form, "")
                
        self.pushButton_2 = QtWidgets.QPushButton(self.static_media_form)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(lambda x: ConfigData.choose_file(MainWindow, self.media_file, "mailing_media_file"))
        self.verticalLayout_5.addWidget(self.pushButton_2)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.static_lang_form = QtWidgets.QWidget()
        self.static_lang_form.setGeometry(QtCore.QRect(0, 0, 480, 190))
        self.static_lang_form.setObjectName("static_lang_form")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.static_lang_form)
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.static_lang_content = MyTextEdit("static_lang_content", self.static_lang_form)

        self.verticalLayout_10.addWidget(self.static_lang_content)
        self.static_work.addItem(self.static_lang_form, "")
        self.horizontalLayout_8.addWidget(self.static_work)
        
        self.tabWidget_3.addTab(self.tab_static, "")
        
        self.tab_channel = QtWidgets.QWidget()
        self.tab_channel.setObjectName("tab_channel")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab_channel)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.channel_work = QtWidgets.QToolBox(self.tab_channel)
        self.channel_work.setMinimumSize(QtCore.QSize(500, 277))
        self.channel_work.setMaximumSize(QtCore.QSize(669, 16777215))
        self.channel_work.setObjectName("channel_work")
        self.page_8 = QtWidgets.QWidget()
        self.page_8.setGeometry(QtCore.QRect(0, 0, 480, 190))
        self.page_8.setObjectName("page_8")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.page_8)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_13 = QtWidgets.QLabel(self.page_8)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 2, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.page_8)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 0, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.page_8)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 3, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.page_8)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 1, 0, 1, 1)

        self.channel_btn_url = MyLineEdit("channel_btn_url", self.page_8)
        self.gridLayout.addWidget(self.channel_btn_url, 3, 2, 1, 1)

        self.channel_title = MyLineEdit("channel_title", self.page_8)
        self.gridLayout.addWidget(self.channel_title, 0, 2, 1, 1)

        self.channel_description = MyLineEdit("channel_description", self.page_8)
        self.gridLayout.addWidget(self.channel_description, 1, 2, 1, 1)

        self.channel_btn_text = MyLineEdit("channel_btn_text", self.page_8)
        self.gridLayout.addWidget(self.channel_btn_text, 2, 2, 1, 1)
        
        self.horizontalLayout_10.addLayout(self.gridLayout)
        self.channel_work.addItem(self.page_8, "")
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setGeometry(QtCore.QRect(0, 0, 480, 211))
        self.page_6.setObjectName("page_6")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.page_6)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        
        self.channel_text_content = MyTextEdit("channel_text_content", self.page_6)
        
        self.horizontalLayout_12.addWidget(self.channel_text_content)
        self.channel_work.addItem(self.page_6, "")
        self.page_7 = QtWidgets.QWidget()
        self.page_7.setGeometry(QtCore.QRect(0, 0, 480, 211))
        self.page_7.setObjectName("page_7")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.page_7)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.page_7)
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(ConfigData.get("mailing_media_file")))
        self.label_4.setScaledContents(True)
        self.label_4.setMaximumSize(100,100)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.pushButton_3 = QtWidgets.QPushButton(self.page_7)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(lambda x: ConfigData.choose_file(MainWindow, self.label_4, "mailing_media_file"))
        
        self.verticalLayout_4.addWidget(self.pushButton_3)
        self.horizontalLayout_11.addLayout(self.verticalLayout_4)
        self.channel_work.addItem(self.page_7, "")
        self.horizontalLayout_7.addWidget(self.channel_work)
        self.tabWidget_3.addTab(self.tab_channel, "")
        self.tab_real_II = QtWidgets.QWidget()
        self.tab_real_II.setObjectName("tab_real_II")
        self.tabWidget_3.addTab(self.tab_real_II, "")
        self.account_data_form.addWidget(self.tabWidget_3)
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_21 = QtWidgets.QLabel(self)
        self.label_21.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName("label_21")
        self.verticalLayout_13.addWidget(self.label_21)
        self.tabWidget_2 = QtWidgets.QTabWidget(self)
        self.tabWidget_2.setObjectName("tabWidget_2")
        
        self.tab_14 = QtWidgets.QWidget()
        self.tab_14.setObjectName("tab_14")
        self.verticalLayout_20 = QtWidgets.QVBoxLayout(self.tab_14)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.toolBox_7 = QtWidgets.QToolBox(self.tab_14)
        self.toolBox_7.setObjectName("toolBox_7")
        self.page_19 = QtWidgets.QWidget()
        self.page_19.setGeometry(QtCore.QRect(0, 0, 478, 204))
        self.page_19.setObjectName("page_19")
        self.verticalLayout_18 = QtWidgets.QVBoxLayout(self.page_19)
        self.verticalLayout_18.setObjectName("verticalLayout_18")

        self.answer_static_text_content = MyTextEdit("answer_static_text_content", self.page_19)
        
        self.verticalLayout_18.addWidget(self.answer_static_text_content)
        self.toolBox_7.addItem(self.page_19, "")
        self.page_22 = QtWidgets.QWidget()
        self.page_22.setGeometry(QtCore.QRect(0, 0, 478, 173))
        self.page_22.setObjectName("page_22")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.page_22)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.answer_file = QtWidgets.QLabel(self.page_22)
        self.answer_file.setText("")
        self.answer_file.setObjectName("answer_file")
        self.answer_file.setPixmap(QtGui.QPixmap(ConfigData.get("answer_media_file")))
        self.answer_file.setScaledContents(True)
        self.answer_file.setMaximumSize(100,100)
        self.verticalLayout_6.setAlignment(QtCore.Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.answer_file)
        self.pushButton_4 = QtWidgets.QPushButton(self.page_22)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(lambda x: ConfigData.choose_file(MainWindow, self.answer_file, "answer_media_file"))
        
        self.verticalLayout_6.addWidget(self.pushButton_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout_6)
        self.toolBox_7.addItem(self.page_22, "")
        self.page_21 = QtWidgets.QWidget()
        self.page_21.setGeometry(QtCore.QRect(0, 0, 478, 204))
        self.page_21.setObjectName("page_21")
        self.verticalLayout_23 = QtWidgets.QVBoxLayout(self.page_21)
        self.verticalLayout_23.setObjectName("verticalLayout_23")

        self.answer_static_lang_content = MyTextEdit("answer_static_lang_content", self.page_21)
        
        self.verticalLayout_23.addWidget(self.answer_static_lang_content)
        self.toolBox_7.addItem(self.page_21, "")
        self.verticalLayout_20.addWidget(self.toolBox_7)
        self.tabWidget_2.addTab(self.tab_14, "")
        self.tab_15 = QtWidgets.QWidget()
        self.tab_15.setObjectName("tab_15")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.tab_15)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.toolBox_6 = QtWidgets.QToolBox(self.tab_15)
        self.toolBox_6.setObjectName("toolBox_6")
        self.page_17 = QtWidgets.QWidget()
        self.page_17.setGeometry(QtCore.QRect(0, 0, 478, 231))
        self.page_17.setObjectName("page_17")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.page_17)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        
        self.prompt_text_content = MyTextEdit("prompt_text_content", self.page_17)
        
        self.verticalLayout_15.addWidget(self.prompt_text_content)
        self.toolBox_6.addItem(self.page_17, "")
        self.page_18 = QtWidgets.QWidget()
        self.page_18.setGeometry(QtCore.QRect(0, 0, 478, 231))
        self.page_18.setObjectName("page_18")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.page_18)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.clear_history_base = QtWidgets.QCheckBox(self.page_18)
        self.clear_history_base.setObjectName("clear_history_base")
        
        self.clear_history_base.setChecked(
            ConfigData.get("clear_history_base")
        )
        self.clear_history_base.clicked.connect(
            lambda x: ConfigData.update(
                "clear_history_base",
                self.clear_history_base.isChecked()
                )
        )
        
        self.gridLayout_5.addWidget(self.clear_history_base, 0, 0, 1, 1)
        self.use_have_prompt = QtWidgets.QCheckBox(self.page_18)
        self.use_have_prompt.setObjectName("use_have_prompt")
        
        self.use_have_prompt.setChecked(
            ConfigData.get("use_have_prompt")
        )
        self.use_have_prompt.clicked.connect(
            lambda x: ConfigData.update(
                "use_have_prompt",
                self.use_have_prompt.isChecked()
                )
        )
        
        self.gridLayout_5.addWidget(self.use_have_prompt, 1, 0, 1, 1)
        self.verticalLayout_17.addLayout(self.gridLayout_5)
        self.toolBox_6.addItem(self.page_18, "")
        self.verticalLayout_16.addWidget(self.toolBox_6)
        self.tabWidget_2.addTab(self.tab_15, "")
        self.tab_16 = QtWidgets.QWidget()
        self.tab_16.setObjectName("tab_16")
        self.verticalLayout_21 = QtWidgets.QVBoxLayout(self.tab_16)
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.label = QtWidgets.QLabel(self.tab_16)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_21.addWidget(self.label)
        self.tabWidget_2.addTab(self.tab_16, "")
        self.tab_17 = QtWidgets.QWidget()
        self.tab_17.setObjectName("tab_17")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.tab_17)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.label_2 = QtWidgets.QLabel(self.tab_17)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_22.addWidget(self.label_2)
        self.tabWidget_2.addTab(self.tab_17, "")
        self.verticalLayout_13.addWidget(self.tabWidget_2)
        self.account_data_form.addLayout(self.verticalLayout_13)
        self.gridLayout_8.addLayout(self.account_data_form, 0, 1, 1, 1)
        
        self.start_btn = self.StartButton()
        
        self.gridLayout_8.addWidget(self.start_btn, 1, 0, 1, 3)
        self.verticalLayout_25.addLayout(self.gridLayout_8)

        self.label_15.setText(_translate("MainWindow", "Таргет"))
        self.variation_target_user.setText(_translate("MainWindow", "по юзерам"))
        self.variation_target_chat.setText(_translate("MainWindow", "по чатам"))
        self.variation_base_user.setText(_translate("MainWindow", "база с юзерами"))
        self.variation_base_chat.setText(_translate("MainWindow", "база с чатами"))
        self.use_have_base.setText(_translate("MainWindow", "Использовать имеющиеся"))
        self.pushButton_5.setText(_translate("MainWindow", "PushButton"))
        self.label_22.setText(_translate("MainWindow", "Доп. настройки"))
        self.uniq_profile.setText(_translate("MainWindow", "Уникализировать"))
        self.slow_mode.setText(_translate("MainWindow", "Слоу мод"))
        self.translate_fio.setText(_translate("MainWindow", "Перевод Имён и Фамилий"))
        self.label_23.setText(_translate("MainWindow", "Запуск аккаунта"))
        self.start_now.setText(_translate("MainWindow", "Запустить сразу"))
        # self.account_list_title.setText(_translate("MainWindow", "Аккаунты"))
        # __sortingEnabled = self.account_list_content.isSortingEnabled()
        # self.account_list_content.setSortingEnabled(False)
        # item = self.account_list_content.item(0)
        # item.setText(_translate("MainWindow", "1 Account"))
        # item = self.account_list_content.item(1)
        # item.setText(_translate("MainWindow", "2 Account"))
        # self.account_list_content.setSortingEnabled(__sortingEnabled)
        self.variation_work_title.setText(_translate("MainWindow", "Режим работы"))
        self.static_work.setItemText(self.static_work.indexOf(self.static_text_form), _translate("MainWindow", "Текст"))
        self.pushButton_2.setText(_translate("MainWindow", "Добавить файл"))
        self.static_work.setItemText(self.static_work.indexOf(self.static_media_form), _translate("MainWindow", "Медиа"))
        self.static_work.setItemText(self.static_work.indexOf(self.static_lang_form), _translate("MainWindow", "Мультиязычность"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_static), _translate("MainWindow", "Статичный"))
        self.label_13.setText(_translate("MainWindow", "Текст кнопки"))
        self.label_12.setText(_translate("MainWindow", "Заголовок"))
        self.label_11.setText(_translate("MainWindow", "URL кнопка"))
        self.label_14.setText(_translate("MainWindow", "Описание"))
        self.channel_work.setItemText(self.channel_work.indexOf(self.page_8), _translate("MainWindow", "Данные канала"))
        self.channel_work.setItemText(self.channel_work.indexOf(self.page_6), _translate("MainWindow", "Текст"))
        self.pushButton_3.setText(_translate("MainWindow", "PushButton"))
        self.channel_work.setItemText(self.channel_work.indexOf(self.page_7), _translate("MainWindow", "Медиа"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_channel), _translate("MainWindow", "Через канал"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_real_II), _translate("MainWindow", "Живое общение"))
        self.label_21.setText(_translate("MainWindow", "Вариант ответов"))
        self.toolBox_7.setItemText(self.toolBox_7.indexOf(self.page_19), _translate("MainWindow", "Текст"))
        self.pushButton_4.setText(_translate("MainWindow", "Добавить файл"))
        self.toolBox_7.setItemText(self.toolBox_7.indexOf(self.page_22), _translate("MainWindow", "Медиа"))
        self.toolBox_7.setItemText(self.toolBox_7.indexOf(self.page_21), _translate("MainWindow", "Мультиязычность"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_14), _translate("MainWindow", "Фиксированным текстом"))
        self.toolBox_6.setItemText(self.toolBox_6.indexOf(self.page_17), _translate("MainWindow", "Промпт"))
        self.clear_history_base.setText(_translate("MainWindow", "Очистить историю"))
        self.use_have_prompt.setText(_translate("MainWindow", "Использовать промпт из settings"))
        self.toolBox_6.setItemText(self.toolBox_6.indexOf(self.page_18), _translate("MainWindow", "Доп. настройки"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_15), _translate("MainWindow", "Нейронкой"))
        self.label.setText(_translate("MainWindow", "Сообщения направленные нашему аккаунту от других будут направлены в отдельный раздел"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_16), _translate("MainWindow", "Своим ответом"))
        self.label_2.setText(_translate("MainWindow", "Сообщения будут оставаться без ответа."))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_17), _translate("MainWindow", "Без автоответчика"))

        self.static_work.setCurrentIndex(1) # TODO тут тоже нужно настроить стартовый индекс
        self.channel_work.setCurrentIndex(0) # TODO тут тоже нужно настроить стартовый индекс
        self.toolBox_7.setCurrentIndex(1) # TODO тут тоже нужно настроить стартовый индекс
        self.toolBox_6.setCurrentIndex(1) # TODO тут тоже нужно настроить стартовый индекс
        self.tabWidget_3.setCurrentIndex(
            ConfigData.get("variation_mailing")
        )
        self.tabWidget_3.currentChanged.connect(
            lambda x: ConfigData.update(
                "variation_mailing",
                self.tabWidget_3.currentIndex()
            )
        )
        self.tabWidget_2.setCurrentIndex(
            ConfigData.get("variation_answer")
        )
        self.tabWidget_2.currentChanged.connect(
            lambda x: ConfigData.update(
                "variation_answer",
                self.tabWidget_2.currentIndex()
            )
        )
        
    class AccountList(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.account_list_form = QtWidgets.QVBoxLayout()
            self.account_list_form.setSpacing(0)
            self.account_list_form.setObjectName("account_list_form")
            
            self.add_content_accs()

            self.setLayout(self.account_list_form)
            
        def clear_layout(self, layout: QtWidgets.QVBoxLayout|QtWidgets.QHBoxLayout):
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                layout.removeItem(item)

        def create_label(self, layout: QtWidgets.QVBoxLayout):
            account_list_title = QtWidgets.QLabel(self)
            account_list_title.setText("Аккаунты")
            account_list_title.setLayoutDirection(QtCore.Qt.LeftToRight)
            account_list_title.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
            account_list_title.setObjectName("account_list_title")
            
            layout.addWidget(account_list_title)

        def add_content_accs(
            self,
            materials: list[dict] = []
            ):
            self.clear_layout(self.account_list_form)
            self.create_label(self.account_list_form)
            if len(materials) == 0:
                pass
            else:
                for account_data in materials:
                    logger.debug(account_data)
                    account_widget = AccountWidget(account_data)
                    self.account_list_form.addWidget(account_widget)

                self.account_list_form.addStretch(1) # Добавляем растяжку, чтобы виджеты прижимались к верху
                
    class StartButton(QtWidgets.QPushButton):
        
        button_new_task = QtCore.pyqtSignal(dict)
        
        def __init__(self):
            super().__init__()
            self.setText("START")
            self.setObjectName("start_btn")
            self.clicked.connect(self.start_work)
            self.loop = None
            self.thread = None

        def start_work(self):
            # if self.loop is None or not self.loop.is_running():
            #     self.loop = asyncio.new_event_loop()
            #     asyncio.set_event_loop(self.loop)
            #     self.thread = threading.Thread(target=self.loop.run_forever, daemon=True) # daemon=True
            #     self.thread.start()
            # asyncio.run_coroutine_threadsafe(StartWork().start(), self.loop)
            # with open(accounts_file, "r", encoding="utf-8") as file:
            #     account_data: dict = json.loads(file.read())
            # logger.debug(account_data)

            start_data = StartWork().start()
            
            if start_data: self.button_new_task.emit(start_data)

        def closeEvent(self, event):
            if self.loop and self.loop.is_running():
                tasks = asyncio.all_tasks(self.loop)
                for task in tasks:
                    task.cancel()  # Отменяем все задачи
                self.loop.stop() # останавливаем цикл событий
                self.thread.join()
                self.loop.close()
                self.loop = None
            super().closeEvent(event)


class ProgressPage(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        self.max_column = 20
        
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        progress_container = QtWidgets.QWidget()
        self.base_layout = QtWidgets.QVBoxLayout(progress_container)
        
        scroll_area.setWidget(progress_container)
        QtWidgets.QVBoxLayout(self).addWidget(scroll_area)
        
        self.create_all_progress_blocks()
    
    def add_head(
        self,
        index: int,
        task: 'Tasks' # type: ignore
        ) -> None:
        number_task = QtWidgets.QLabel(f"№ {index}")
        status = QtWidgets.QLabel(task['status'])
        title = QtWidgets.QLabel(task['title'])
        description = QtWidgets.QLabel(task['description'])
        
        head_container = QtWidgets.QWidget()
        head_layout = QtWidgets.QHBoxLayout(head_container)
        
        head_layout.addWidget(number_task)
        head_layout.addWidget(status)
        head_layout.addWidget(title)
        head_layout.addWidget(description)
        
        self.base_layout.addWidget(head_container)

    def add_mailing_answer_widget(
        self,
        task: 'Tasks' # type: ignore
        ) -> None:
        max_column = 10
        mailing_answer_container = QtWidgets.QWidget()
        mailing_answer_layout = QtWidgets.QHBoxLayout(mailing_answer_container)
        
        mailing_container = QtWidgets.QWidget()
        mailing_layout = QtWidgets.QGridLayout(mailing_container)
        
        answer_container = QtWidgets.QWidget()
        answer_layout = QtWidgets.QGridLayout(answer_container)
        
        mailing_answer_layout.addWidget(mailing_container)
        mailing_answer_layout.addWidget(answer_container)

        title_mailing = QtWidgets.QLabel(
            "Данные для рассылки"
        )
        title_mailing.setAlignment(QtCore.Qt.AlignCenter)
        mailing_layout.addWidget(
            title_mailing,
            0,0,1,max_column
            )
        title_answer = QtWidgets.QLabel(
            "Данные для ответов"
        )
        title_answer.setAlignment(QtCore.Qt.AlignCenter)
        answer_layout.addWidget(
            title_answer,
            0,0,1,max_column
            )
        
        mailing_image_container = QtWidgets.QWidget()
        mailing_image = QtWidgets.QLabel(mailing_image_container)
        mailing_image.setPixmap(
            QtGui.QPixmap(
                os.path.join(
                    photos_folder,
                    task['media_file']
                    ) if task['media_file'] else os.path.join(
                        images_folder,
                        "default.jpg"
                        )
                    )
                )

        mailing_image.setScaledContents(True)
        mailing_image.setMaximumSize(100,100)

        mailing_layout.addWidget(
            mailing_image_container,
            1,0,max_column//2,max_column//2
            )
        
        answer_image_container = QtWidgets.QWidget()
        answer_image = QtWidgets.QLabel(answer_image_container)
        answer_image.setPixmap(
            QtGui.QPixmap(
                os.path.join(
                    photos_folder,
                    task['answer_media']
                    ) if task['answer_media'] else os.path.join(
                        images_folder,
                        "default.jpg"
                        )
                    )
                )

        answer_image.setScaledContents(True)
        answer_image.setMaximumSize(100,100)

        answer_layout.addWidget(
            answer_image_container,
            1,0,max_column//2,max_column//2
            )
        
        mailing_scroll_area = QtWidgets.QScrollArea()
        mailing_scroll_area.setWidgetResizable(True)

        mailing_data_container = QtWidgets.QWidget()
        mailing_data_layout = QtWidgets.QVBoxLayout(mailing_data_container)
        
        mailing_scroll_area.setWidget(mailing_data_container)
        
        text_default = QtWidgets.QLabel(
            f"Default Text: {task['text_default']}"
        )
        mailing_data_layout.addWidget(text_default)
        lang_default = QtWidgets.QLabel(
            f"Lang Text: {task['text_lang']}"
        )
        mailing_data_layout.addWidget(lang_default)
        neuro_mod = QtWidgets.QLabel(
            f"Neuro Mod: {task['neuro_mod']}"
        )
        mailing_data_layout.addWidget(neuro_mod)
        translate_fio = QtWidgets.QLabel(
            f"Translate FIO: {task['translate_fio']}"
        )
        mailing_data_layout.addWidget(translate_fio)

        mailing_layout.addWidget(
            mailing_scroll_area,
            1,5,max_column//2,max_column//2
            )
        
        answer_scroll_area = QtWidgets.QScrollArea()
        answer_scroll_area.setWidgetResizable(True)

        answer_data_container = QtWidgets.QWidget()
        answer_data_layout = QtWidgets.QVBoxLayout(answer_data_container)

        answer_scroll_area.setWidget(answer_data_container)

        answer_text_default = QtWidgets.QLabel(
            f"Default Text: {task['answer_text_default']}"
        )
        answer_data_layout.addWidget(answer_text_default)
        answer_text_lang = QtWidgets.QLabel(
            f"Lang Text: {task['answer_text_lang']}"
        )
        answer_data_layout.addWidget(answer_text_lang)
        answer_neuro_mod = QtWidgets.QLabel(
            f"Neuro Mod: {task['answer_neuro_mod']}"
        )
        answer_data_layout.addWidget(answer_neuro_mod)
        answer_language_matching = QtWidgets.QLabel(
            f"Translate FIO: {task['answer_language_matching']}"
        )
        answer_data_layout.addWidget(answer_language_matching)
        answer_prompt = QtWidgets.QLabel(
            f"Answer Prompt: {task['answer_prompt']}"
        )
        answer_data_layout.addWidget(answer_prompt)
        
        answer_layout.addWidget(
            answer_scroll_area,
            1,5,max_column//2,max_column//2
            )
        
        self.base_layout.addWidget(mailing_answer_container)

    def download_file_connect(
        self,
        ) -> None:
        """
        Скачиваем файл
        """

    def change_file_connect(
        self,
        ) -> None:
        """
        Смениваем файл
        """

    def add_base_widget(
        self,
        task: 'Tasks' # type: ignore
        ) -> None:
        name_var_target = QtWidgets.QLabel(
            f"Variation Target: {task['variation_target']}"
            )
        name_var_base = QtWidgets.QLabel(
            f"Variation Base: {task['variation_base']}"
            )
        name_base_file = QtWidgets.QLabel(
            f"Base File Name: {task['base_file']}"
            )
        
        change_file = QtWidgets.QPushButton("Change")
        change_file.clicked.connect(
            self.change_file_connect
        )
        
        download_file = QtWidgets.QPushButton("Download")
        download_file.clicked.connect(
            self.download_file_connect
        )
        
        base_container = QtWidgets.QWidget()
        base_layout = QtWidgets.QHBoxLayout(base_container)
        
        base_layout.addWidget(name_var_target)
        base_layout.addWidget(name_var_base)
        base_layout.addWidget(name_base_file)
        base_layout.addWidget(change_file)
        base_layout.addWidget(download_file)
        
        self.base_layout.addWidget(base_container)

    def add_other_settings_channel_server_widget(
        self,
        task: 'Tasks' # type: ignore
        ) -> None:
        o_s_ch_s_container = QtWidgets.QWidget()
        o_s_ch_s_layout = QtWidgets.QHBoxLayout(o_s_ch_s_container)
        
        other_settings_container = QtWidgets.QWidget()
        other_settings_layout = QtWidgets.QVBoxLayout(other_settings_container)
        
        o_s_ch_s_layout.addWidget(other_settings_container)
        
        name_var_target = QtWidgets.QLabel(
            "Другие настройки"
            )
        use_have_base = QtWidgets.QLabel(
            f"Использовать имеющиеся кантакты: {task['use_have_base']}"
            )
        use_have_prompt = QtWidgets.QLabel(
            f"Использовать промат из конфига: {task['use_have_prompt']}"
            )
        clear_history_base = QtWidgets.QLabel(
            f"Очистить историю общения: {task['clear_history_base']}"
            )
        uniq_profile = QtWidgets.QLabel(
            f"Уникализация пользователя: {task['uniq_profile']}"
            )
        slow_mode = QtWidgets.QLabel(
            f"Слоу мод: {task['slow_mode']}"
            )
        system_version = QtWidgets.QLabel(
            f"Версия Системы: {task['system_version']}"
            )
        waiting_time_sending_user = QtWidgets.QLabel(
            f"Ожидание между сообщений одному юзеру: {task['waiting_time_sending_user']}"
            )
        waiting_time_sending_chst = QtWidgets.QLabel(
            f"Ожидание между сообщений в один чат: {task['waiting_time_sending_chst']}"
            )
        repeats = QtWidgets.QLabel(
            f"Повторений цикла: {task['repeats']}"
            )
        wait_msg_chats = QtWidgets.QLabel(
            f"Ожидание после инвайта: {task['wait_msg_chats']}"
            )
        time_to_start = QtWidgets.QLabel(
            f"Время запуска: {task['time_to_start']}"
            )
        
        other_settings_layout.addWidget(name_var_target)
        other_settings_layout.addWidget(use_have_base)
        other_settings_layout.addWidget(use_have_prompt)
        other_settings_layout.addWidget(clear_history_base)
        other_settings_layout.addWidget(uniq_profile)
        other_settings_layout.addWidget(slow_mode)
        other_settings_layout.addWidget(system_version)
        other_settings_layout.addWidget(waiting_time_sending_user)
        other_settings_layout.addWidget(waiting_time_sending_chst)
        other_settings_layout.addWidget(repeats)
        other_settings_layout.addWidget(wait_msg_chats)
        other_settings_layout.addWidget(time_to_start)
        
        channel_container = QtWidgets.QWidget()
        channel_layout = QtWidgets.QVBoxLayout(channel_container)
        
        o_s_ch_s_layout.addWidget(channel_container)
        
        name_channel = QtWidgets.QLabel(
            "Настройки канала"
            )
        channel_title = QtWidgets.QLabel(
            f"Заголовок: {task['channel_title']}"
            )
        channel_description = QtWidgets.QLabel(
            f"Описание: {task['channel_description']}"
            )
        channel_btn_text = QtWidgets.QLabel(
            f"Текст кнопки: {task['channel_btn_text']}"
            )
        channel_btn_url = QtWidgets.QLabel(
            f"URL кнопки: {task['channel_btn_url']}"
            )
        
        channel_layout.addWidget(name_channel)
        channel_layout.addWidget(channel_title)
        channel_layout.addWidget(channel_description)
        channel_layout.addWidget(channel_btn_text)
        channel_layout.addWidget(channel_btn_url)
        
        server_container = QtWidgets.QWidget()
        server_layout = QtWidgets.QVBoxLayout(server_container)
        
        o_s_ch_s_layout.addWidget(server_container)
        
        name_server = QtWidgets.QLabel(
            "Данные сервера"
            )
        server_connection_id = QtWidgets.QLabel(
            f"ID Соеденения: {task['connection_id']}"
            )
        server_local_adress = QtWidgets.QLabel(
            f"Локальный Адрес: {task['local_adress']}"
            )
        server_server_adress = QtWidgets.QLabel(
            f"Адрес Сервера: {task['server_adress']}"
            )
        server_server_port = QtWidgets.QLabel(
            f"Порт Сервера: {task['server_port']}"
            )
        
        server_layout.addWidget(name_server)
        server_layout.addWidget(server_connection_id)
        server_layout.addWidget(server_local_adress)
        server_layout.addWidget(server_server_adress)
        server_layout.addWidget(server_server_port)
        
        self.base_layout.addWidget(o_s_ch_s_container)

    def add_wait_sleep_widget(
        self,
        time_delay: 'TimeDilay', # type: ignore
        sleep_blocks: list['SleepBlocks'] # type: ignore
        ) -> None:        
        wait_sleep_container = QtWidgets.QWidget()
        wait_sleep_layout = QtWidgets.QHBoxLayout(wait_sleep_container)
        
        base_wait_container = QtWidgets.QWidget()
        base_wait_layout = QtWidgets.QVBoxLayout(base_wait_container)
        
        wait_sleep_layout.addWidget(base_wait_container)
        
        base_title_wait = QtWidgets.QLabel(
            "Промежутки для ожиданий между действий"
        )
        base_wait_layout.addWidget(base_title_wait)

        wait_container = QtWidgets.QWidget()
        wait_layout = QtWidgets.QGridLayout(wait_container)
        
        base_wait_layout.addWidget(wait_container)
        
        prof_uniq_wait = QtWidgets.QLabel(
            (
                "После уникализации профиля\n"
                f"{time_delay['prof_uniq_min']} - {time_delay['prof_uniq_min']}"
                )
        )
        wait_layout.addWidget(
            prof_uniq_wait,
            0,0,1,5
            )
        pars_chat_wait = QtWidgets.QLabel(
            (
                "После уникализации профиля\n"
                f"{time_delay['pars_chat_min']} - {time_delay['pars_chat_min']}"
                )
        )
        wait_layout.addWidget(
            pars_chat_wait,
            1,0,1,5
            )
        send_msg_user_wait = QtWidgets.QLabel(
            (
                "Между сообщений юзеру\n"
                f"{time_delay['send_msg_user_min']} - {time_delay['send_msg_user_min']}"
                )
        )
        wait_layout.addWidget(
            send_msg_user_wait,
            2,0,1,5
            )
        send_msg_chat_wait = QtWidgets.QLabel(
            (
                "Между сообщений в чат\n"
                f"{time_delay['send_msg_chat_min']} - {time_delay['send_msg_chat_min']}"
                )
        )
        wait_layout.addWidget(
            send_msg_chat_wait,
            3,0,1,5
            )
        invite_wait = QtWidgets.QLabel(
            (
                "Между инвайтами\n"
                f"{time_delay['invite_min']} - {time_delay['invite_min']}"
                )
        )
        wait_layout.addWidget(
            invite_wait,
            4,0,1,5
            )
        read_history_wait = QtWidgets.QLabel(
            (
                "Между чтением истории\n"
                f"{time_delay['read_history_min']} - {time_delay['read_history_min']}"
                )
        )
        wait_layout.addWidget(
            read_history_wait,
            0,5,1,5
            )
        error_delay_entity_wait = QtWidgets.QLabel(
            (
                "После получения ошибок\n"
                f"{time_delay['error_delay_entity_min']} - {time_delay['error_delay_entity_min']}"
                )
        )
        wait_layout.addWidget(
            error_delay_entity_wait,
            1,5,1,5
            )
        auto_responder_static_wait = QtWidgets.QLabel(
            (
                "Перед статичным автоответом\n"
                f"{time_delay['auto_responder_static_min']} - {time_delay['auto_responder_static_min']}"
                )
        )
        wait_layout.addWidget(
            auto_responder_static_wait,
            2,5,1,5
            )
        auto_responder_II_wait = QtWidgets.QLabel(
            (
                "Перед автоответа нейронкой\n"
                f"{time_delay['auto_responder_II_min']} - {time_delay['auto_responder_II_min']}"
                )
        )
        wait_layout.addWidget(
            auto_responder_II_wait,
            3,5,1,5
            )
        after_launch_wait = QtWidgets.QLabel(
            (
                "Перед стартом\n"
                f"{time_delay['after_launch_min']} - {time_delay['after_launch_min']}"
                )
        )
        wait_layout.addWidget(
            after_launch_wait,
            4,5,1,5
            )
        between_steps_wait = QtWidgets.QLabel(
            (
                "Между шагов\n"
                f"{time_delay['between_steps_min']} - {time_delay['between_steps_min']}"
                )
        )
        wait_layout.addWidget(
            between_steps_wait,
            0,10,1,5
            )
        peerflooderror_wait = QtWidgets.QLabel(
            (
                "После ошибки о спаме\n"
                f"{time_delay['peerflooderror_min']} - {time_delay['peerflooderror_min']}"
                )
        )
        wait_layout.addWidget(
            peerflooderror_wait,
            1,10,1,5
            )
        work_acc_wait = QtWidgets.QLabel(
            (
                "После работы софта\n"
                f"{time_delay['work_acc_min']} - {time_delay['work_acc_min']}"
                )
        )
        wait_layout.addWidget(
            work_acc_wait,
            2,10,1,5
            )
        
        base_sleep_container = QtWidgets.QWidget()
        base_sleep_layout = QtWidgets.QVBoxLayout(base_sleep_container)
        
        base_title_wait = QtWidgets.QLabel(
            "Промежутки для снов"
        )
        base_sleep_layout.addWidget(base_title_wait)
        
        sleep_container = QtWidgets.QWidget()
        sleep_layout = QtWidgets.QVBoxLayout(sleep_container)
        
        base_sleep_layout.addWidget(sleep_container)
        
        wait_sleep_layout.addWidget(base_sleep_container)
                
        for index, sleep_block in enumerate(sleep_blocks, start=1):
            index_sleep = QtWidgets.QLabel(
                f"№ {index}"
            )
            sleep_layout.addWidget(index_sleep)
            start_end_sleep = QtWidgets.QLabel(
                f"{sleep_block['start']} - {sleep_block['end']}"
            )
            sleep_layout.addWidget(start_end_sleep)
           
        self.base_layout.addWidget(wait_sleep_container)

    def switch_tab(
        self,
        account_data_stack_container: QtWidgets.QStackedWidget,
        # switch_tab_button: QtWidgets.QPushButton
        ):
        """
        Функция переключения вкладок по нажатию кнопки
        """
        current_index = account_data_stack_container.currentIndex()
        new_index = (current_index + 1) % 2  # Переключение между 0 и 1
        account_data_stack_container.setCurrentIndex(new_index)
        # switch_tab_button.setText(f"Переключить на {'информацию' if new_index == 0 else 'данные'}")

    def add_progress(
        self,
        materials: list['Materials'], # type: ignore
        account_progress: list['AccountProgress'] # type: ignore
        ) -> None:
        account_progress_container = QtWidgets.QWidget()
        account_progress_layout = QtWidgets.QGridLayout(account_progress_container)
        
        title_block = QtWidgets.QLabel("Progress")
        
        account_progress_layout.addWidget(
            title_block,
            0,0,1,self.max_column
        )

        account_data_tab_container = QtWidgets.QTabWidget()
        
        for material, account_progres in zip(materials, account_progress):
            """
            добавляем вкладку
            """
            account_data_stack_container = QtWidgets.QStackedWidget()
            switch_tab_button_one = QtWidgets.QPushButton("Switch")
            switch_tab_button_one.clicked.connect(
                lambda x: self.switch_tab(account_data_stack_container)
            )
                        
            account_data_tab_container.addTab(
                account_data_stack_container,
                str(material['name'])
                )
            
            # NOTE создаем виджет для приобретенной/изменяемой инфы
            account_info_container = QtWidgets.QWidget()
            account_info_layout = QtWidgets.QGridLayout(account_info_container)
            
            # NOTE создаем виджет для стартовой инфы
            base_account_data_container = QtWidgets.QWidget()
            scroll_account_data = QtWidgets.QScrollArea(base_account_data_container)
            scroll_account_data.setWidgetResizable(True)

            account_data_container = QtWidgets.QWidget()
            account_data_layout = QtWidgets.QVBoxLayout(account_data_container)
            
            scroll_account_data.setWidget(account_data_container)
            
            # NOTE при старте закидываем обложку
            image_profile = QtWidgets.QLabel()
            image_profile.setPixmap(
                QtGui.QPixmap(
                    os.path.join(
                        account_folder, 
                        account_progres['account_photo']
                        ) if account_progres['account_photo'] else os.path.join(
                            images_folder, 
                            "default.jpg"
                        )
                    )
                )
            image_profile.setScaledContents(True)
            image_profile.setMaximumSize(100,100)
                
            username_profile = QtWidgets.QLabel(
                    f"UserName: @{account_progres['account_username'] if account_progres['account_username'] else "..."}"
                )
            user_id_profile = QtWidgets.QLabel(
                    f"User ID: {account_progres['account_user_id'] if account_progres['account_user_id'] else "..."}"
                )
            first_name_profile = QtWidgets.QLabel(
                    f"First Name: {account_progres['account_first_name'] if account_progres['account_first_name'] else "..."}"
                )
            last_name_profile = QtWidgets.QLabel(
                    f"Last Name: {account_progres['account_last_name'] if account_progres['account_last_name'] else "..."}"
                )
            description_profile = QtWidgets.QLabel(
                    f"Description: {account_progres['account_description'] if account_progres['account_description'] else "..."}"
                )
            
            invite_profile = QtWidgets.QLabel(
                (
                    "Инвайтов: "
                    f"{str(account_progres['invite'])}"
                    )
                )
            user_pars_profile = QtWidgets.QLabel(
                (
                    "Спаршено: "
                    f"{str(account_progres['user_pars'])}"
                    )
                )
            message_profile = QtWidgets.QLabel(
                (
                    "Отправлено сообщений: "
                    f"{str(account_progres['message'])}"
                    )
                )
            wait_profile = QtWidgets.QLabel(
                (
                    "Ожиданий: "
                    f"{str(account_progres['wait'])}"
                    )
                )
            auto_responder_profile = QtWidgets.QLabel(
                (
                    "Ответов: "
                    f"{str(account_progres['auto_responder'])}"
                    )
                )
            
            errors_profile = QtWidgets.QLabel(
                (
                    "Errors: "
                    f"{str(account_progres['errors'])}"
                    )
                )
            
            account_info_layout.addWidget(
                image_profile,
                0,0,5,5
            )
            account_info_layout.addWidget(
                username_profile,
                0,5,1,5
            )
            account_info_layout.addWidget(
                user_id_profile,
                1,5,1,5
            )
            account_info_layout.addWidget(
                first_name_profile,
                2,5,1,5
            )
            account_info_layout.addWidget(
                last_name_profile,
                3,5,1,5
            )
            account_info_layout.addWidget(
                description_profile,
                4,5,1,5
            )
            account_info_layout.addWidget(
                invite_profile,
                0,10,1,4 # NOTE забираем один столбик для кнопки
            )
            account_info_layout.addWidget(
                switch_tab_button_one,
                0,14,1,1 # NOTE забираем один столбик для кнопки
            )
            account_info_layout.addWidget(
                user_pars_profile,
                1,10,1,5
            )
            account_info_layout.addWidget(
                message_profile,
                2,10,1,5
            )
            account_info_layout.addWidget(
                wait_profile,
                3,10,1,5
            )
            account_info_layout.addWidget(
                auto_responder_profile,
                4,10,1,5
            )
            account_info_layout.addWidget(
                errors_profile,
                5,0,3,self.max_column
            )
            
            head_account_data = QtWidgets.QWidget()
            head_account_data_layout = QtWidgets.QHBoxLayout(head_account_data)
            
            label_start = QtWidgets.QLabel(
                f"          Данные для Старта"
                )
            
            head_account_data_layout.addWidget(label_start)
            switch_tab_button_two = QtWidgets.QPushButton("Switch")
            switch_tab_button_two.clicked.connect(
                lambda x: self.switch_tab(account_data_stack_container)
            )

            head_account_data_layout.addWidget(switch_tab_button_two)
            
            account_data_layout.addWidget(head_account_data)
            
            material_id = QtWidgets.QLabel(
                f"ID: {material['id']}"
                )
            account_data_layout.addWidget(material_id)
            material_session_path = QtWidgets.QLabel(
                f"Session Path: {material['session_path']}"
                )
            account_data_layout.addWidget(material_session_path)
            material_name = QtWidgets.QLabel(
                f"Name: {material['name']}"
                )
            account_data_layout.addWidget(material_name)
            material_status = QtWidgets.QLabel(
                f"Status: {material['status']}"
                )
            account_data_layout.addWidget(material_status)
            material_two_fa = QtWidgets.QLabel(
                f"Two Fa: {material['two_fa']}"
                )
            account_data_layout.addWidget(material_two_fa)
            material_api_id = QtWidgets.QLabel(
                f"Api ID: {material['api_id']}"
                )
            account_data_layout.addWidget(material_api_id)
            material_api_hash = QtWidgets.QLabel(
                f"Api Hash: {material['api_hash']}"
                )
            account_data_layout.addWidget(material_api_hash)
            material_app_version = QtWidgets.QLabel(
                f"App Version: {material['app_version']}"
                )
            account_data_layout.addWidget(material_app_version)
            material_device_model = QtWidgets.QLabel(
                f"Device: {material['device_model']}"
                )
            account_data_layout.addWidget(material_device_model)
            material_lang_code = QtWidgets.QLabel(
                f"Lang: {material['lang_code']}"
                )
            account_data_layout.addWidget(material_lang_code)
            material_system_lang_code = QtWidgets.QLabel(
                f"System Lang: {material['system_lang_code']}"
                )
            account_data_layout.addWidget(material_system_lang_code)

            label_uniq = QtWidgets.QLabel(
                f"\n          Данные для уникализации\n"
                )
            account_data_layout.addWidget(label_uniq)
            material_account_photo = QtWidgets.QLabel(
                f"Photo: {material['account_photo']}"
                )
            account_data_layout.addWidget(material_account_photo)
            material_account_first_name = QtWidgets.QLabel(
                f"First Name: {material['account_first_name']}"
                )
            account_data_layout.addWidget(material_account_first_name)
            material_account_last_name = QtWidgets.QLabel(
                f"Last Name: {material['account_last_name']}"
                )
            account_data_layout.addWidget(material_account_last_name)
            material_account_username = QtWidgets.QLabel(
                f"UserName: {material['account_username']}"
                )
            account_data_layout.addWidget(material_account_username)
            material_account_description = QtWidgets.QLabel(
                f"Description: {material['account_description']}"
                )
            account_data_layout.addWidget(material_account_description)
            material_proxy = QtWidgets.QLabel(
                f"Proxy: {material['proxy']}"
                )
            account_data_layout.addWidget(material_proxy)
            
            account_data_stack_container.addWidget(account_info_container)
            account_data_stack_container.addWidget(account_data_container)
            account_data_stack_container.setCurrentIndex(0)
        
        base_all_progress_block = QtWidgets.QWidget()
        all_progress_block = QtWidgets.QVBoxLayout(base_all_progress_block)
        
        invite_profiles = QtWidgets.QLabel(
            f"Общее кол-во Инвайтов: {sum([account_progres['invite'] for account_progres in account_progress])}"
            )
        user_pars_profiles = QtWidgets.QLabel(
            f"Общее кол-во Спаршено: {sum([account_progres['user_pars'] for account_progres in account_progress])}"
            )
        message_profiles = QtWidgets.QLabel(
            f"Общее кол-во Отправлено сообщений: {sum([account_progres['message'] for account_progres in account_progress])}"
            )
        wait_profiles = QtWidgets.QLabel(
            f"Общее кол-во Ожиданий: {sum([account_progres['wait'] for account_progres in account_progress])}"
            )
        auto_responder_profiles = QtWidgets.QLabel(
            f"Общее кол-во Ответов: {sum([account_progres['auto_responder'] for account_progres in account_progress])}"
            )
        
        all_progress_block.addWidget(invite_profiles)
        all_progress_block.addWidget(user_pars_profiles)
        all_progress_block.addWidget(message_profiles)
        all_progress_block.addWidget(wait_profiles)
        all_progress_block.addWidget(auto_responder_profiles)
        
        account_progress_layout.addWidget(
            account_data_tab_container,
            0,0,10,15
        )
        account_progress_layout.addWidget(
            base_all_progress_block,
            0,15,10,5
        )
        
        self.base_layout.addWidget(account_progress_container)

    def clear_layout(self, layout: QtWidgets.QVBoxLayout|QtWidgets.QHBoxLayout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            layout.removeItem(item)

    def create_all_progress_blocks(
        self,
        datas_tasks: list[dict] = []
        ):
        self.clear_layout(self.base_layout)
        if len(datas_tasks) == 0:
            pass
        else:
            for index, data_task in enumerate(datas_tasks, start=1):
                logger.debug(data_task)
                
                materials = data_task['materials']
                account_progress = data_task['account_progress']
                task = data_task['task']
                time_delay = data_task['time_delay']
                sleep_blocks = data_task['sleep_blocks']

                if (
                    not materials and
                    not account_progress and
                    not task and
                    not time_delay and
                    not sleep_blocks
                ):
                    continue
                    
                
                self.add_head(index,task)
                self.add_progress(materials,account_progress)
                self.add_base_widget(task)
                self.add_mailing_answer_widget(task)
                self.add_other_settings_channel_server_widget(task)
                self.add_wait_sleep_widget(time_delay,sleep_blocks)

            self.base_layout.addStretch(1)


class AccountsPage(QtWidgets.QWidget):

    button_add_account = QtCore.pyqtSignal(dict)
    button_delete_account = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # NOTE БАЗА
        base_scroll_area = QtWidgets.QScrollArea()
        base_scroll_area.setWidgetResizable(True)

        base_container = QtWidgets.QWidget()
        base_layout = QtWidgets.QHBoxLayout(base_container)
        # ////////////
        
        # NOTE Форма для нынешних аккаунтов
        now_accounts_container = QtWidgets.QWidget()
        self.now_accounts_layout = QtWidgets.QVBoxLayout(now_accounts_container)
        
        left_scroll_area = QtWidgets.QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        
        left_scroll_area.setWidget(now_accounts_container)
        base_layout.addWidget(left_scroll_area)

        # NOTE Форма для добавления аккаунтов
        add_account_container = QtWidgets.QWidget()
        self.add_account_layout = QtWidgets.QVBoxLayout(add_account_container)
        
        right_scroll_area = QtWidgets.QScrollArea()
        right_scroll_area.setWidgetResizable(True)
        
        right_scroll_area.setWidget(add_account_container)
        base_layout.addWidget(right_scroll_area)
        
        # ////////////
        base_scroll_area.setWidget(base_container)
        QtWidgets.QVBoxLayout(self).addWidget(base_scroll_area)
        
        self.create_now_accounts_form()
        self.create_add_account_form()

    def clear_layout(self, layout: QtWidgets.QVBoxLayout|QtWidgets.QHBoxLayout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            layout.removeItem(item)

    def create_now_accounts_form(
        self,
        materials: list[dict] = []
        ):
        """
        Создаем форму для управления существующими аккаунтами.
        """
        self.clear_layout(self.now_accounts_layout)
        if len(materials) == 0:
            pass
        else:
            for index, material in enumerate(materials):
                # NOTE старт
                account_container = QtWidgets.QWidget()
                account_layout = QtWidgets.QVBoxLayout(account_container)

                head_container = QtWidgets.QWidget()
                head_layout = QtWidgets.QHBoxLayout(head_container)

                content_container = QtWidgets.QWidget()
                content_layout = QtWidgets.QGridLayout(content_container)

                account_layout.addWidget(head_container)
                account_layout.addWidget(content_container)
                self.now_accounts_layout.addWidget(account_container)

                # NOTE наполняем шапку
                material_index = QtWidgets.QLabel(
                    f"№ {index}"
                    )
                head_layout.addWidget(material_index)

                material_name = QtWidgets.QLabel(
                    f"Name: {material['name']}"
                    )
                head_layout.addWidget(material_name)

                material_phone = QtWidgets.QLabel(
                    f"Phone: {material['phone']}"
                    )
                head_layout.addWidget(material_phone)

                material_id = QtWidgets.QLabel(
                    f"ID in Base: {material['id']}"
                    )
                head_layout.addWidget(material_id)
                
                delete_btn = QtWidgets.QPushButton(
                    "Удалить Аккаунт"
                )
                delete_btn.clicked.connect(
                    lambda x: self.delete_account(material['id'])
                )
                head_layout.addWidget(delete_btn)
                
                # NOTE наполняем данными аккаунта
                base_title = QtWidgets.QLabel(
                    f"\n          Основные данные\n"
                    )
                content_layout.addWidget(
                    base_title,
                    0,0,1,10
                    )

                material_session_path = QtWidgets.QLabel(
                    f"Session Path: {material['session_path']}"
                    )
                content_layout.addWidget(
                    material_session_path,
                    1,0,1,5
                    )
                material_status = QtWidgets.QLabel(
                    f"Status: {material['status']}"
                    )
                content_layout.addWidget(
                    material_status,
                    2,0,1,5
                    )
                material_two_fa = QtWidgets.QLabel(
                    f"Two Fa: {material['two_fa']}"
                    )
                content_layout.addWidget(
                    material_two_fa,
                    3,0,1,5
                    )
                material_api_id = QtWidgets.QLabel(
                    f"Api ID: {material['api_id']}"
                    )
                content_layout.addWidget(
                    material_api_id,
                    4,0,1,5
                    )
                material_api_hash = QtWidgets.QLabel(
                    f"Api Hash: {material['api_hash']}"
                    )
                content_layout.addWidget(
                    material_api_hash,
                    1,5,1,5
                    )
                material_app_version = QtWidgets.QLabel(
                    f"App Version: {material['app_version']}"
                    )
                content_layout.addWidget(
                    material_app_version,
                    2,5,1,5
                    )
                material_device_model = QtWidgets.QLabel(
                    f"Device: {material['device_model']}"
                    )
                content_layout.addWidget(
                    material_device_model,
                    3,5,1,5
                    )
                material_lang_code = QtWidgets.QLabel(
                    f"Lang/System Lang: {material['lang_code']}/{material['system_lang_code']}"
                    )
                content_layout.addWidget(
                    material_lang_code,
                    4,5,1,5
                    )

                label_uniq = QtWidgets.QLabel(
                    f"\n          Данные для уникализации\n"
                    )
                content_layout.addWidget(
                    label_uniq,
                    0,10,1,5
                    )
                material_account_photo = QtWidgets.QLabel(
                    f"Photo: {material['account_photo']}"
                    )
                content_layout.addWidget(
                    material_account_photo,
                    1,10,1,5
                    )
                material_account_first_name = QtWidgets.QLabel(
                    f"First Name: {material['account_first_name']}"
                    )
                content_layout.addWidget(
                    material_account_first_name,
                    2,10,1,5
                    )
                material_account_last_name = QtWidgets.QLabel(
                    f"Last Name: {material['account_last_name']}"
                    )
                content_layout.addWidget(
                    material_account_last_name,
                    3,10,1,5
                    )
                material_account_username = QtWidgets.QLabel(
                    f"UserName: {material['account_username']}"
                    )
                content_layout.addWidget(
                    material_account_username,
                    4,10,1,5
                    )
                material_account_description = QtWidgets.QLabel(
                    f"Description: {material['account_description']}"
                    )
                content_layout.addWidget(
                    material_account_description,
                    5,10,1,5
                    )

                material_proxy = QtWidgets.QLabel(
                    f"Proxy: {material['proxy']}"
                    )
                content_layout.addWidget(
                    material_proxy,
                    6,0,1,15
                    )

        self.now_accounts_layout.addStretch(1)

    def input_form_text(
        self,
        content_layout,
        title: str,
        name: str,
        *,
        random: bool = False
        ):
        data_container = QtWidgets.QWidget()
        data_layout = QtWidgets.QHBoxLayout(data_container)
        
        input_form = QtWidgets.QLineEdit()
        
        label = QtWidgets.QLabel(title)
        input = AccountLineEdit(name,input_form)
        
        data_layout.addWidget(label)
        data_layout.addWidget(input)
        
        if random:
            add_button = QtWidgets.QPushButton(
                "RANDOM"
            )
            add_button.clicked.connect(
                lambda x: input.setText('1')
            )
            add_button.clicked.connect(
                lambda x: AccountData.update(
                    name,
                    "1"
                )
            )
            
            data_layout.addWidget(add_button)
        
        content_layout.addWidget(data_container)

    def input_form_file(
        self,
        content_layout,
        title: str,
        key: str,
        filter: str,
        *,
        is_folder: bool = False,
        random: bool = False
        ):
        data_container = QtWidgets.QWidget()
        data_layout = QtWidgets.QHBoxLayout(data_container)
        
        title_ = QtWidgets.QLabel(f"{title}:")
        image = QtWidgets.QLabel()
        image.setPixmap(
            QtGui.QPixmap(
                AccountData.get(key,True)
                )
        )
        image.setScaledContents(True)
        image.setMaximumSize(50,50)

        # add_button_container = QtWidgets.QWidget()
        add_button = QtWidgets.QPushButton(
            f"Загрузить {title}"
        )
        add_button.clicked.connect(
            lambda x: AccountData.choose_file(
                data_container,
                image,
                key,
                filter
            )
        )
        
        data_layout.addWidget(title_)
        data_layout.addWidget(image)
        data_layout.addWidget(add_button)
        
        if random:
            add_button = QtWidgets.QPushButton(
                "RANDOM"
            )
            add_button.clicked.connect(
                lambda x: AccountData.update(
                    "account_photo",
                    "1"
                )
            )

            data_layout.addWidget(add_button)
        
        content_layout.addWidget(data_container)

    def create_add_account_form(
        self
        ):
        """
        Форма для добавления аккаунтов.
        """
        add_form_container = QtWidgets.QWidget()
        add_form_layout = QtWidgets.QVBoxLayout(add_form_container)

        head_container = QtWidgets.QLabel(
            "Форма для добавления аккаунта"
        )

        content_container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_container)
        
        self.input_form_text(content_layout,"Name:","name")
        self.input_form_text(content_layout,"Description:","description")

        self.input_form_file(content_layout,"Session","session_path","Session Files (*.session)")
        self.input_form_file(content_layout,"Archives","session_path","Archives (*.zip *.rar)")
        self.input_form_text(content_layout,"Phone:","phone")
        self.input_form_text(content_layout,"Two Fa:","twoFA")
        self.input_form_text(content_layout,"Api ID:","app_id")
        self.input_form_text(content_layout,"Api Hash:","app_hash")
        self.input_form_text(content_layout,"App Version:","app_version")
        self.input_form_text(content_layout,"Device:","device_model")
        self.input_form_text(content_layout,"Lang:","lang_code")
        self.input_form_text(content_layout,"System Lang:","system_lang_code")

        self.input_form_file(content_layout,"Account Photo","account_photo","Image Files (*.png *.jpg)",random=True)
        self.input_form_text(content_layout,"First Name:","account_first_name",random=True)
        self.input_form_text(content_layout,"Last Name:","account_last_name",random=True)
        self.input_form_text(content_layout,"UserName:","account_username",random=True)
        self.input_form_text(content_layout,"Description:","account_description",random=True)
        self.input_form_text(content_layout,"Proxy:","proxy")
        
        footer_container = QtWidgets.QWidget()
        footer_layout = QtWidgets.QHBoxLayout(footer_container)

        self.add_button = QtWidgets.QPushButton(
            "Save"
        )
        # self.add_button.clicked.connect(self.add_button_signal.emit)
        self.add_button.clicked.connect(self.save_in_base)
        footer_layout.addWidget(self.add_button)

        add_form_layout.addWidget(head_container)
        add_form_layout.addWidget(content_container)
        add_form_layout.addWidget(footer_container)
        self.add_account_layout.addWidget(add_form_container)
        
    def save_in_base(self):
        with open(accounts_file, "r", encoding="utf-8") as file:
            account_data: dict = json.loads(file.read())
        logger.debug(account_data)
        
        self.button_add_account.emit(account_data)
        
    def delete_account(
        self,
        material_id: int
        ):
        """
        Создаем форму для управления существующими аккаунтами.
        """
        self.button_delete_account.emit(material_id)

        
class SettingsPage(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        base_scroll_area = QtWidgets.QScrollArea()
        base_scroll_area.setWidgetResizable(True)

        base_container = QtWidgets.QWidget()
        self.now_settings_layout = QtWidgets.QVBoxLayout(base_container)

        base_scroll_area.setWidget(base_container)
        QtWidgets.QVBoxLayout(self).addWidget(base_scroll_area)
        
        self.create_edit_settings_form()
        self.now_settings_layout.addStretch(1)

    def add_note(
        self,
        note_layout: QtWidgets.QHBoxLayout,
        input: QtWidgets.QLineEdit,
        list_keys: list[str]
        ):
        """
        Добавляем запись с данными.
        """

    def input_edit_config(
        self,
        content_layout: QtWidgets.QVBoxLayout,
        title: str,
        list_keys: list[str],
        *,
        add_btn: bool = False,
        # default: typing.Optional[str] = None
        ):
        data_container = QtWidgets.QWidget()
        data_layout = QtWidgets.QHBoxLayout(data_container)
        
        input_form = QtWidgets.QLineEdit()
        
        label = QtWidgets.QLabel(title)
        input = SettingsLineEdit(list_keys,input_form)
        
        data_layout.addWidget(label)
        data_layout.addWidget(input)
        
        if add_btn:
            note_container = QtWidgets.QWidget()
            note_layout = QtWidgets.QHBoxLayout(note_container)
            
            add_button = QtWidgets.QPushButton(
                "Добавить запись"
            )
            add_button.clicked.connect(
                lambda x: self.add_note(note_layout,input,list_keys)
            )
            
            data_layout.addWidget(add_button)
            content_layout.addWidget(data_container)
            content_layout.addWidget(note_container)
        else:
            content_layout.addWidget(data_container)

    def create_edit_settings_form(
        self
        ) -> None:
        add_form_container = QtWidgets.QWidget()
        add_form_layout = QtWidgets.QVBoxLayout(add_form_container)

        head_container = QtWidgets.QLabel(
            "Форма для редактирования конфиг файла"
        )
        add_form_layout.addWidget(head_container)

        content_container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_container)
        
        time_dilay_container = QtWidgets.QLabel(
            "Стартовые данные для ожиданий между действий"
        )
        content_layout.addWidget(time_dilay_container)

        self.input_edit_config(content_layout,"После уникализации профиля:",list_keys=["time_dilay","prof_uniq"])
        self.input_edit_config(content_layout,"Между парсингом:",list_keys=["time_dilay","pars_chat"])
        self.input_edit_config(content_layout,"Между сообщений юзеру:",list_keys=["time_dilay","send_msg_user"])
        self.input_edit_config(content_layout,"Между сообщений в чат:",list_keys=["time_dilay","send_msg_chat"])
        self.input_edit_config(content_layout,"Между инвайтами:",list_keys=["time_dilay","invite"])
        self.input_edit_config(content_layout,"Между чтением истории:",list_keys=["time_dilay","read_history"])
        self.input_edit_config(content_layout,"После получения ошибок:",list_keys=["time_dilay","error_delay_entity"])
        self.input_edit_config(content_layout,"Перед статичным автоответом:",list_keys=["time_dilay","auto_responder_static"])
        self.input_edit_config(content_layout,"Перед автоответа нейронкой:",list_keys=["time_dilay","auto_responder_II"])
        self.input_edit_config(content_layout,"Перед стартом:",list_keys=["time_dilay","after_launch"])
        self.input_edit_config(content_layout,"Между шагов:",list_keys=["time_dilay","between_steps"])
        self.input_edit_config(content_layout,"После ошибки о спаме:",list_keys=["time_dilay","peerflooderror"])
        self.input_edit_config(content_layout,"После работы софта",list_keys=["time_dilay","work_acc"])
        
        self.input_edit_config(content_layout,"Промежутки для снов:",list_keys=["time_dilay","sleep_blocks"],add_btn=True)
        
        time_dilay_container = QtWidgets.QLabel(
            "Другие настройки"
        )
        content_layout.addWidget(time_dilay_container)

        self.input_edit_config(content_layout,"Настройки парсинга юзеров:",list_keys=["pars_users"],add_btn=True)
        
        self.input_edit_config(content_layout,"Версия системы:",list_keys=["const","system_version"])
        self.input_edit_config(content_layout,"Повторений:",list_keys=["settings_mailing_chats","repeats"])
        self.input_edit_config(content_layout,"Проверка после инвайта:",list_keys=["settings_mailing_chats","wait_msg_chats"])
        self.input_edit_config(content_layout,"Промпт:",list_keys=["settings_II","prompt"])
        self.input_edit_config(content_layout,"Ожидание после сообщения юзеру:",list_keys=["settings_dilay_mailing_to_target","user"])
        self.input_edit_config(content_layout,"Ожидание после сообщения чату:",list_keys=["settings_dilay_mailing_to_target","chat"])
        self.input_edit_config(content_layout,"Список кнопок для нажатия после инвайта:",list_keys=["black_list_buttons"])
        self.input_edit_config(content_layout,"Список кнопок для перехода по url:",list_keys=["url_list_buttons"])
        
        add_form_layout.addWidget(content_container)
        self.now_settings_layout.addWidget(add_form_container)


class AccountListWidget(QtWidgets.QWidget):
    """
    Виджет для отображения списка аккаунтов на странице с общением.
    """
    account_selected = QtCore.pyqtSignal(str)  # Сигнал для выбора аккаунта

    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.account_list = QtWidgets.QListWidget()
        self.account_list.itemClicked.connect(self.on_account_selected)
        self.layout.addWidget(self.account_list)

    def add_accounts(self, account_datas: list['Materials.__dict__']): # type: ignore
        """
        Обновляем список аккаунтов.
        """
        self.account_list.clear()
        for account_data in account_datas:
            item = QtWidgets.QListWidgetItem(account_data['phone'])
            self.account_list.addItem(item)

    def on_account_selected(self, item):
        """
        Обрабатывает выбор аккаунта.
        После чего отправляются данные на сервер
        для обновления списка с чатами.
        """
        self.account_selected.emit(item.text())


class ChatListWidget(QtWidgets.QWidget):
    """
    Виджет для отображения списка чатов для аккаунта.
    """
    chat_selected = QtCore.pyqtSignal(dict)  # Сигнал для выбора чата

    def __init__(self, active_account_phone: str):
        super().__init__()
        self.active_account_phone = active_account_phone

        self.layout = QtWidgets.QVBoxLayout(self)
        self.chat_list = QtWidgets.QListWidget()
        self.chat_list.itemClicked.connect(self.on_chat_selected)
        self.layout.addWidget(self.chat_list)

    def create_chat_list(self, chat_datas: list['ChatRooms.__dict__']): # type: ignore
        """
        Обновляем список аккаунтов.
            QtCore.Qt.DisplayRole: Роль для отображаемого текста.

            QtCore.Qt.DecorationRole: Роль для иконки.

            QtCore.Qt.ToolTipRole: Роль для всплывающей подсказки.
        """
        self.chat_list.clear()
        for chat_data in chat_datas:
            item = QtWidgets.QListWidgetItem(chat_data.get("chat_name"))
            item.setData(QtCore.Qt.UserRole, chat_data.get("chat_id"))
            
            if chat_data.get("chat_type") == "user":
                item.setIcon(QtGui.QIcon(
                    os.path.join(images_folder,"user.png")
                ))
            elif chat_data.get("chat_type") == "chat":
                item.setIcon(QtGui.QIcon(
                    os.path.join(images_folder,"chat.png")
                    ))
            elif chat_data.get("chat_type") == "channel":
                item.setIcon(QtGui.QIcon(
                    os.path.join(images_folder,"channel.png")
                    ))
            
            self.chat_list.addItem(item)

    def on_chat_selected(self, item: QtWidgets.QListWidgetItem):
        """
        Обрабатывает выбор аккаунта.
        После чего отправляются данные на сервер
        для обновления списка с чатами.
        """
        self.chat_selected.emit(
            {
                "account_phone": self.active_account_phone,
                "chat_id": item.data(QtCore.Qt.UserRole)
            }
        )

    def set_active_account_phone(self, phone: str):
        """
        Обновляет активный аккаунт.
        """
        self.active_account_phone = phone


class ChatWidget(QtWidgets.QWidget):
    """
    Виджет для отображения сообщений и ввода текста.
    """
    message_sent = QtCore.pyqtSignal(dict)  # Сигнал для отправки текстового сообщения

    def __init__(self, active_account_phone: str, active_chat_id: str):
        super().__init__()
        self.active_account_phone = active_account_phone
        self.active_chat_id = active_chat_id
        self.file_path = None

        self.layout = QtWidgets.QVBoxLayout(self)

        # Виджет для отображения сообщений
        self.chat_display = QtWidgets.QTextEdit()
        self.chat_display.setReadOnly(True)  # Запрещаем редактирование
        self.layout.addWidget(self.chat_display)

        # Виджет для ввода сообщения и отправки медиа
        self.input_layout = QtWidgets.QHBoxLayout()
        self.message_input = QtWidgets.QLineEdit()
        self.send_button = QtWidgets.QPushButton("Отправить")
        self.send_button.clicked.connect(self.on_send_clicked)
        self.attach_button = QtWidgets.QPushButton("Прикрепить")
        self.attach_button.clicked.connect(self.on_attach_clicked)
        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.attach_button)
        self.input_layout.addWidget(self.send_button)
        self.layout.addLayout(self.input_layout)

    def create_chat_history(self, data: list['Messages.__dict__']): # type: ignore
        """
        Обновляет историю сообщений.
        """
        self.chat_display.clear()
        for message in data:
            self.add_message_to_chat(message)

    def add_message_to_chat(self, message: 'Messages.__dict__'): # type: ignore
        """
        Добавляет сообщение в чат.
        """
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        # Определяем выравнивание и стиль сообщения
        alignment_str = "right" if message['my'] else "left"
        username = "Вы" if message['my'] else message['username']

        # Создаем HTML-таблицу для управления выравниванием
        html_content = f"""
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="{alignment_str}" style="padding: 5px;">
                    <b>{username}</b>
                </td>
            </tr>
        """

        # Добавляем медиафайл, если он есть
        if message['media_type'] and message['media_content']:
            if message['media_type'] in ["photo", "video"]:
                html_content += f"""
                <tr>
                    <td align="{alignment_str}" style="padding: 5px;">
                        <img src="{message['media_content']}" width="200"/>
                    </td>
                </tr>
                """
            elif message['media_type'] == "audio":
                html_content += f"""
                <tr>
                    <td align="{alignment_str}" style="padding: 5px;">
                        <audio controls src="{message['media_content']}"></audio>
                    </td>
                </tr>
                """
            else:
                html_content += f"""
                <tr>
                    <td align="{alignment_str}" style="padding: 5px;">
                        <img src="not_found.png" width="100"/>
                    </td>
                </tr>
                """

        # Добавляем текст сообщения
        html_content += f"""
        <tr>
            <td align="{alignment_str}" style="padding: 5px;">
                {message['text']}
            </td>
        </tr>
        </table>
        <br>
        """

        # Вставляем HTML в QTextEdit
        cursor.insertHtml(html_content)

    def on_send_clicked(self):
        """
        Обрабатывает нажатие кнопки "Отправить".
        """
        message = self.message_input.text()
        
        if message or self.file_path:
            self.message_sent.emit(
                {
                    "account_phone": self.active_account_phone,
                    "chat_id": self.active_chat_id,
                    "message": message,
                    "file_path": self.file_path
                }
            )
        
        if message: self.message_input.clear()

    def on_attach_clicked(self):
        """
        Обрабатывает нажатие кнопки "Прикрепить".
        """
        self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Выберите файл", 
            "", 
            "Images (*.png *.jpg);;Videos (*.mp4);;Audio (*.mp3)"
            )

    def set_active_account_phone(self, phone: str):
        """
        Обновляет активный аккаунт.
        """
        self.active_account_phone = phone

    def set_active_chat_id(self, chat_id: str):
        """
        Обновляет активный аккаунт.
        """
        self.active_chat_id = chat_id


class ChatPage(QtWidgets.QMainWindow):
    """
    Главное окно приложения.
    """
    def __init__(self):
        super().__init__()
        self.active_account_phone = None
        self.active_chat_id = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Чат")
        self.setGeometry(100, 100, 800, 600)

        # Основной макет
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)

        # Виджет списка аккаунтов
        self.account_list_widget = AccountListWidget()
        self.main_layout.addWidget(self.account_list_widget, 1)

        # Виджет списка чатов
        self.chat_list_widget = ChatListWidget(
            self.active_account_phone
        )
        self.main_layout.addWidget(self.chat_list_widget, 1)

        # Виджет чата
        self.chat_widget = ChatWidget(
            self.active_account_phone,
            self.active_chat_id
            )
        self.main_layout.addWidget(self.chat_widget, 3)

        # Устанавливаем центральный виджет
        self.setCentralWidget(self.main_widget)

        # Соединяем сигнал выбора аккаунта с методом обновления
        self.account_list_widget.account_selected.connect(self.update_active_account_phone)
        self.chat_list_widget.chat_selected.connect(self.update_active_chat_id)

    def update_active_account_phone(self, phone: str):
        self.active_account_phone = phone
        self.chat_list_widget.set_active_account_phone(phone)
        self.chat_widget.set_active_account_phone(phone)

    def update_active_chat_id(self, data: dict):
        self.active_chat_id = data['chat_id']
        self.chat_widget.set_active_chat_id(data['chat_id'])

