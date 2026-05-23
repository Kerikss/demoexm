from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from config import LOGO_PATH, ICON_PATH
from database import get_user
from windows.product_window import ProductWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обувь - Вход в систему")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Times New Roman';")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        logo_label = QLabel()
        pixmap = QPixmap(LOGO_PATH)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio))
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        layout.addSpacing(20)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.login_edit)
        layout.addWidget(self.password_edit)

        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet("background-color: #00FA9A; padding: 8px;")
        self.login_btn.clicked.connect(self.do_login)

        self.guest_btn = QPushButton("Войти как гость")
        self.guest_btn.setStyleSheet("background-color: #7FFF00; padding: 8px;")
        self.guest_btn.clicked.connect(self.guest_login)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.guest_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def do_login(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        user = get_user(login, password)
        if user:
            role, full_name = user
            self.open_product_window(role, full_name)
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")

    def guest_login(self):
        self.open_product_window('guest', None)

    def open_product_window(self, role, full_name):
        self.product_win = ProductWindow(role, full_name)
        self.product_win.show()
        self.close()