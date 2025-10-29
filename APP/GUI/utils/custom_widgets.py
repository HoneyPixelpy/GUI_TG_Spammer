import os

from APP.GUI.utils.file_manager import * # images_folder
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np



class ErrorAlert(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
    
    def show_message(
        self,
        title: str,
        message: str
        ) -> None:
        msg = QtWidgets.QMessageBox()
        msg.setWindowIcon(
            QtGui.QIcon(
                os.path.join(
                    images_folder,
                    "ava_logo.png"
                )
            )
        )
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


class NotificationWidget(QtWidgets.QFrame):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.main_window = self.find_main_window(parent)
        self.setup_ui(title, message)
        self.setup_animation()
        
        # Таймер для отслеживания положения главного окна
        self.position_timer = QtCore.QTimer(self)
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.start(100)  # Проверка каждые 100 мс

    def find_main_window(self, parent):
        """Находит главное окно приложения"""
        if parent is None:
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if isinstance(widget, QtWidgets.QMainWindow):
                    return widget
            return None
        return parent.window() if parent else None

    def update_position(self):
        """Обновляет позицию уведомления относительно главного окна"""
        if self.main_window and self.main_window.isVisible():
            main_rect = self.main_window.frameGeometry()
            x = main_rect.right() - self.width() - 20
            y = main_rect.bottom() - self.height() - 20
            self.move(x, y)

    def setup_ui(self, title, message):
        self.setWindowFlags(
            QtCore.Qt.ToolTip | 
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setFixedSize(300, 100)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel#title {
                font-weight: bold;
                font-size: 12px;
                color: #212529;
            }
            QLabel#message {
                font-size: 11px;
                color: #495057;
            }
            QPushButton {
                border: none;
                background: transparent;
                padding: 0;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # Header with title and close button
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout()
        header.setLayout(header_layout)
        
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setObjectName("title")
        header_layout.addWidget(self.title_label)
        
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close_notification)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header)
        
        # Message content
        self.message_label = QtWidgets.QLabel(message)
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Timer for auto-close
        self.close_timer = QtCore.QTimer()
        self.close_timer.setInterval(15000)  # 15 seconds
        self.close_timer.timeout.connect(self.close_notification)
        self.close_timer.start()

    def setup_animation(self):
        # Animation for smooth appearance
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def close_notification(self):
        # Animation for smooth disappearance
        self.animation = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.position_timer.stop()
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def showEvent(self, event):
        self.update_position()  # Первоначальная позиция
        # Позиционируем относительно главного окна приложения
        if self.parent():
            # Если есть родительское окно
            parent_window = self.parent().window() if self.parent() else None
            if parent_window:
                parent_rect = parent_window.frameGeometry()
                x = parent_rect.right() - self.width() - 20
                y = parent_rect.bottom() - self.height() - 20
                self.move(x, y)
        else:
            # Если нет родительского окна, позиционируем относительно активного окна
            main_window = QtWidgets.QApplication.activeWindow()
            if main_window:
                main_rect = main_window.frameGeometry()
                x = main_rect.right() - self.width() - 20
                y = main_rect.bottom() - self.height() - 20
                self.move(x, y)
            else:
                # Если нет активного окна, используем позиционирование по умолчанию
                screen_geo = QtWidgets.QApplication.desktop().availableGeometry()
                x = screen_geo.width() - self.width() - 20
                y = screen_geo.height() - self.height() - 20
                self.move(x, y)
        
        super().showEvent(event)

    def closeEvent(self, event):
        self.position_timer.stop()
        super().closeEvent(event)


class ResultRequestAlert:
    _instance = None  # Статическая переменная для хранения единственного экземпляра
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResultRequestAlert, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.__initialized:
            self.notifications = []
            self.offset = 0
            self.__initialized = True
            # Очистка при завершении приложения
            QtWidgets.QApplication.instance().aboutToQuit.connect(self.cleanup)        

    def cleanup(self):
        for notification in self.notifications[:]:
            notification.close()

    def show_message(self, title, message, parent=None):
        notification = NotificationWidget(title, message, parent)
        notification.show()
        
        # Stack notifications vertically
        if self.notifications:
            last_notification = self.notifications[-1]
            new_pos = last_notification.pos() - QtCore.QPoint(0, notification.height() + 10)
            notification.move(new_pos)
        
        self.notifications.append(notification)
        notification.destroyed.connect(lambda: self.notifications.remove(notification))
        
        # Auto-close after delay
        QtCore.QTimer.singleShot(15000, notification.close_notification)


class MyTextEdit(QtWidgets.QTextEdit):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.setAcceptRichText(True)
        self.load_text()

    def load_text(self):
        """Просто загружает текст из конфига"""
        saved_text = ConfigData.get(self.name)
        if saved_text:
            self.setHtml(saved_text)  # Или setPlainText(), в зависимости от ваших нужд

    def save_text(self):
        """Сохраняет как простой текст без HTML"""
        plain_text = self.toPlainText()
        ConfigData.update(self.name, plain_text)

    def focusOutEvent(self, event):
        """Сохраняем при потере фокуса"""
        self.save_text()
        super().focusOutEvent(event)

    def contextMenuEvent(self, event):
        """Минимальное контекстное меню"""
        menu = self.createStandardContextMenu()
        menu.exec_(event.globalPos())

class MyLineEdit(QtWidgets.QLineEdit):
    def __init__(
            self, 
            name, 
            parent: QtWidgets.QLineEdit
            ):
        super().__init__(parent)
        self.name: str = name
        self.setObjectName(name)
        self.setText(ConfigData.get(name))

    def focusOutEvent(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.FocusOut:
            text = self.text()
            print(f"QLineEdit потерял фокус. Текст: {text}")
            # Сохранение текста в файл или другое действие
            ConfigData.update(self.name,text) # Пример сохранения в файл
        super().focusOutEvent(event)


class AccountLineEdit(QtWidgets.QLineEdit):
    def __init__(
            self, 
            name, 
            parent: QtWidgets.QLineEdit
            ):
        super().__init__(parent)
        self.name: str = name
        self.setObjectName(name)
        self.setText(str(AccountData.get(name)))

    def focusOutEvent(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.FocusOut:
            text = self.text()
            print(f"QLineEdit потерял фокус. Текст: {text}")
            # Сохранение текста в файл или другое действие
            AccountData.update(self.name,text) # Пример сохранения в файл
        super().focusOutEvent(event)


class SettingsLineEdit(QtWidgets.QLineEdit):
    
    def __init__(
            self, 
            list_keys: list[str], 
            parent: QtWidgets.QLineEdit
            ):
        super().__init__(parent)
        self.list_keys = list_keys
        
        setting = SettingsData.get(list_keys)
        
        # if type(setting) == dict:
        #     if setting.get('min'):
        #         logger.debug('min')
        #     else:
        #         logger.debug('dict')
        # elif type(setting) == list[dict]:
        #     logger.debug('list[dict]')
        # elif type(setting) == list:
        #     logger.debug('list')
        
        self.name: str = list_keys[-1]
        self.setObjectName(self.name)
        self.setText(str(setting))
        
    def focusOutEvent(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.FocusOut:
            text = self.text()
            print(f"QLineEdit потерял фокус. Текст: {text}")
            SettingsData.update(self.list_keys,text)
        super().focusOutEvent(event)


class WidgetTools:

    @staticmethod
    def create_circle_pixmap(diameter, color):
        """Создает QPixmap с кругом заданного диаметра и цвета."""
        pixmap = QtGui.QPixmap(diameter, diameter)
        pixmap.fill(QtCore.Qt.transparent) # Заполняем прозрачным цветом, чтобы фон был прозрачным

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing) # Включаем сглаживание для более гладкого круга
        painter.setBrush(QtGui.QBrush(color)) # Устанавливаем цвет кисти
        painter.setPen(QtCore.Qt.NoPen) # Убираем обводку

        center = QtCore.QPoint(diameter // 2, diameter // 2)
        radius = diameter // 2
        painter.drawEllipse(center, radius, radius) # Рисуем круг

        painter.end()
        return pixmap

    @staticmethod
    def pixmap_equal(pixmap1, pixmap2):
        """Сравнивает содержимое двух QPixmap."""
        if pixmap1.size() != pixmap2.size(): return False

        image1 = pixmap1.toImage()
        image2 = pixmap2.toImage()

        # Проверяем, что изображения валидны
        if image1.isNull() or image2.isNull(): return False

        # Получаем данные изображения в формате numpy array
        ptr1 = image1.bits().asstring(image1.byteCount())
        arr1 = np.frombuffer(ptr1, dtype=np.uint8).reshape((image1.height(), image1.width(), image1.depth()//8))

        ptr2 = image2.bits().asstring(image2.byteCount())
        arr2 = np.frombuffer(ptr2, dtype=np.uint8).reshape((image2.height(), image2.width(), image2.depth()//8))

        return np.array_equal(arr1, arr2)



