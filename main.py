import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from windows.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    font = QFont("Times New Roman", 10)
    app.setFont(font)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()