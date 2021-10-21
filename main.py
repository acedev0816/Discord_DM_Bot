from time import sleep
import sys
import threading
# ui
from ui.ui_main import Ui_MainWindow
from ui.ui_settings import Ui_Dialog as Ui_Settings_Dialog
# bot
from bot import Bot
# qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtPrintSupport import *

DISCORD_LOGIN_URL = "https://discord.com/login"
APP_NAME = "Discord DM Bot"
# user = User(settings[0], settings[1], 'https://discord.com/login', settings[2], settings[3], settings[4])
# user.send_message()

class SettingsDialog(QDialog, Ui_Settings_Dialog):
    def __init__(self, parent):
        # setup ui
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        
        # load settings
        self.load_settings()
        # connect
        self.btn_save.clicked.connect(self.slot_save)
        self.btn_close.clicked.connect(self.close)

    def load_settings(self):
        settings = QSettings(APP_NAME, "Bot")
        # email
        email = settings.value("email")
        if email:
            self.le_email.setText(email)
        
        # password
        password = settings.value("password")
        if password:
            self.le_password.setText(password)

        # channel_id
        channel_id = settings.value("channel_id")
        if channel_id:
            self.le_channel.setText(channel_id)
        
        # msg
        msg = settings.value("msg")
        if msg:
            self.te_msg.setPlainText(msg)
        
    def slot_save(self):
        # check email
        email = self.le_email.text().strip()
        if not email:
            QMessageBox.warning(self, APP_NAME, "Please input email.")
            return
        # check password
        password = self.le_password.text().strip()
        if not password:
            QMessageBox.warning(self, APP_NAME, "Please input password.")
            return
        # check channel id
        channel_id = self.le_channel.text().strip()
        if not channel_id:
            QMessageBox.warning(self, APP_NAME, "Please input channel id.")
            return
        # check msg
        msg = self.te_msg.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, APP_NAME, "Please input message.")
            return
        # save to registry
        settings = QSettings(APP_NAME, "Bot")
        settings.setValue("email", email)
        settings.setValue("password", password)
        settings.setValue("channel_id", channel_id)
        settings.setValue("msg", msg)

        self.accept()
 
class MainUi(QMainWindow, Ui_MainWindow):
    log_signal = pyqtSignal(str)
    # member variables
    settings_dialog = None
    bot = None
    bot_thread = None
    def __init__(self, parent):
        # setup ui
        super(MainUi, self).__init__(parent)
        self.setupUi(self)
        
        # set image
        self.lb_logo.setPixmap(QPixmap("./res/logo.png").scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # create objects
        self.settings_dialog = SettingsDialog(self)
        self.bot = Bot('', '',DISCORD_LOGIN_URL, 10, '', '')
        self.bot.log_signal = self.log_signal

        # init ui
        self.setFixedHeight(160)
        self.btn_stop.setEnabled(False)

        # connect
        self.act_settings.triggered.connect(self.slot_settings)
        self.btn_start.clicked.connect(self.slot_start)
        self.btn_stop.clicked.connect(self.slot_stop)
        self.btn_close.clicked.connect(self.slot_close)
        self.bot.log_signal.connect(self.slot_log)

    def slot_start(self):
        # check if bot settings is right
        self.update_settings()
        if not self.bot.is_settings_valid():
            QMessageBox.warning(self, APP_NAME, "Bot settings are not valid. Please check.")
            return

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.setFixedHeight(400)
        self.btn_close.setEnabled(False)
        
        # star thread
        self.thread = threading.Thread(target=self.bot_thread_action)
        self.thread.setDaemon(True)
        self.thread.start()

    def bot_thread_action(self):
        self.bot.running = True
        self.bot.send_message()

    def slot_log(self, msg):
        self.te_log.append(msg)

    def slot_stop(self):
        if not self.bot.running:
            QMessageBox.warning(self, APP_NAME, "Bot settings are not valid. Please check.")
            return

        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.setFixedHeight(160)
        self.btn_close.setEnabled(True)
        
        self.bot.running = False

    def slot_close(self):
        self.close()
        pass

    def update_settings(self):
        self.bot.email = self.settings_dialog.le_email.text()
        self.bot.password = self.settings_dialog.le_password.text()
        self.bot.channel_id = self.settings_dialog.le_channel.text()
        self.bot.msg = self.settings_dialog.te_msg.toPlainText()

    def slot_settings(self):
        if self.settings_dialog.exec_() == QDialog.Accepted:
            self.update_settings()

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("./res/logo.png"))
main_ui = MainUi(None)
main_ui.show()
app.exec_()

