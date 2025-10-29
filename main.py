import asyncio
import sys

from loguru import logger

from APP.GUI.API.websocket import WebSocketApplication
from APP.GUI.main import Ui_MainWindow, QtWidgets
from settings import ip, port


class Application(QtWidgets.QMainWindow):
    def __init__(self, ip: str, port: int):
        super().__init__()
        self.application = Ui_MainWindow().setupUi(self)
        self.websocket = WebSocketApplication(self.application, ip, port)
        logger.success("Создали приложение")
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = Application(ip,port)
    widget.show()
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    asyncio.run(main())
