from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from config import LOGO_PATH, ICON_PATH
from database import get_all_orders, delete_order
from dialogs.order_edit_dialog import OrderEditDialog

class OrdersWindow(QMainWindow):
    def __init__(self, role, full_name=None):
        super().__init__()
        self.role = role
        self.full_name = full_name
        self.setWindowTitle("Обувь - Управление заказами")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(150, 150, 1200, 600)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Times New Roman';")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Верхняя панель
        top_bar = QHBoxLayout()
        logo_label = QLabel()
        pixmap = QPixmap(LOGO_PATH)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(100, 50, Qt.KeepAspectRatio))
        top_bar.addWidget(logo_label)
        top_bar.addStretch()
        if full_name:
            name_label = QLabel(full_name)
            name_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
            top_bar.addWidget(name_label)

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet("background-color: #7FFF00; padding: 5px;")
        back_btn.clicked.connect(self.close)
        top_bar.addWidget(back_btn)

        layout.addLayout(top_bar)

        # Кнопка "Добавить заказ" только для админа
        if self.role == 'Администратор':
            self.add_order_btn = QPushButton("Добавить заказ")
            self.add_order_btn.setStyleSheet("background-color: #00FA9A; padding: 5px;")
            self.add_order_btn.clicked.connect(self.add_order)
            layout.addWidget(self.add_order_btn)

        # Таблица заказов
        self.table = QTableWidget()
        headers = ["ID заказа", "Фамилия", "Имя", "Отчество", "Статус",
                   "Адрес ПВ", "Дата заказа", "Дата доставки", "Код получения"]
        if self.role == 'Администратор':
            headers.append("Действия")
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        if self.role == 'Администратор':
            self.table.doubleClicked.connect(self.edit_order_from_table)

        layout.addWidget(self.table)
        self.load_orders()

    def load_orders(self):
        orders = get_all_orders()
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            order_id, last_name, first_name, middle_name, status, address, order_date, delivery_date, pickup_code = order
            self.table.setItem(row, 0, QTableWidgetItem(str(order_id)))
            self.table.setItem(row, 1, QTableWidgetItem(last_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(first_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(middle_name or ""))
            self.table.setItem(row, 4, QTableWidgetItem(status))
            self.table.setItem(row, 5, QTableWidgetItem(address))
            self.table.setItem(row, 6, QTableWidgetItem(order_date if order_date else ""))
            self.table.setItem(row, 7, QTableWidgetItem(delivery_date if delivery_date else ""))
            self.table.setItem(row, 8, QTableWidgetItem(pickup_code))

            if self.role == 'Администратор':
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 25)
                edit_btn.clicked.connect(lambda checked, oid=order_id: self.edit_order(oid))
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(30, 25)
                delete_btn.clicked.connect(lambda checked, oid=order_id: self.delete_order(oid))
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.addStretch()
                self.table.setCellWidget(row, 9, btn_widget)

        self.table.resizeColumnsToContents()

    def add_order(self):
        self.edit_dialog = OrderEditDialog(self, order_id=None, role=self.role)
        self.edit_dialog.finished.connect(self.on_edit_finished)
        self.edit_dialog.show()

    def edit_order(self, order_id):
        self.edit_dialog = OrderEditDialog(self, order_id=order_id, role=self.role)
        self.edit_dialog.finished.connect(self.on_edit_finished)
        self.edit_dialog.show()

    def edit_order_from_table(self, index):
        row = index.row()
        order_id_item = self.table.item(row, 0)
        if order_id_item:
            self.edit_order(int(order_id_item.text()))

    def delete_order(self, order_id):
        reply = QMessageBox.question(self, "Подтверждение удаления",
                                     f"Удалить заказ №{order_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                delete_order(order_id)
                QMessageBox.information(self, "Успех", "Заказ удалён.")
                self.load_orders()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить заказ:\n{str(e)}")

    def on_edit_finished(self):
        self.load_orders()