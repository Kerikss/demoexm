from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QHBoxLayout, QLabel, QMessageBox, QDialogButtonBox,
                             QSpinBox, QDateEdit)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QHeaderView
from database import (get_clients, get_order_statuses, get_pickup_points,
                      get_next_order_id, save_order, get_order_by_id,
                      get_all_products_for_combo)

class OrderEditDialog(QDialog):
    def __init__(self, parent=None, order_id=None, role=None):
        super().__init__(parent)
        self.parent = parent
        self.order_id = order_id
        self.role = role
        self.is_new = (order_id is None)
        self.setWindowTitle("Новый заказ" if self.is_new else f"Редактирование заказа №{order_id}")
        self.setModal(True)
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout(self)

        # Основная форма
        form = QFormLayout()

        # Номер заказа
        self.order_id_edit = QLineEdit()
        if not self.is_new:
            self.order_id_edit.setReadOnly(True)
        else:
            self.order_id_edit.setPlaceholderText("Автоматически (оставьте пустым)")
        form.addRow("Номер заказа:", self.order_id_edit)

        # Клиент
        self.client_combo = QComboBox()
        self.client_combo.addItem("-- Выберите клиента --", None)
        for uid, name in get_clients():
            self.client_combo.addItem(name, uid)
        form.addRow("Клиент:", self.client_combo)

        # Статус
        self.status_combo = QComboBox()
        for sid, sname in get_order_statuses():
            self.status_combo.addItem(sname, sid)
        form.addRow("Статус:", self.status_combo)

        # Адрес ПВ
        self.address_combo = QComboBox()
        for pid, addr in get_pickup_points():
            self.address_combo.addItem(addr, pid)
        form.addRow("Пункт выдачи:", self.address_combo)

        # Даты
        self.order_date_edit = QDateEdit()
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setDate(QDate.currentDate())
        form.addRow("Дата заказа:", self.order_date_edit)

        self.delivery_date_edit = QDateEdit()
        self.delivery_date_edit.setCalendarPopup(True)
        self.delivery_date_edit.setDate(QDate.currentDate().addDays(30))
        form.addRow("Дата доставки:", self.delivery_date_edit)

        # Код получения
        self.pickup_code_edit = QLineEdit()
        self.pickup_code_edit.setPlaceholderText("Автогенерация")
        form.addRow("Код получения:", self.pickup_code_edit)

        layout.addLayout(form)

        # Таблица товаров в заказе
        layout.addWidget(QLabel("Состав заказа:"))
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Артикул", "Наименование", "Количество", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.items_table)

        # Кнопки управления позициями
        items_btns = QHBoxLayout()
        add_item_btn = QPushButton("Добавить товар")
        add_item_btn.clicked.connect(self.add_order_item)
        items_btns.addWidget(add_item_btn)
        items_btns.addStretch()
        layout.addLayout(items_btns)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.items = []  # список [product_id, name, quantity]

        if not self.is_new:
            self.load_order_data()

    def load_order_data(self):
        order, items = get_order_by_id(self.order_id)
        if order:
            customer_id, status_id, point_id, order_date, delivery_date, pickup_code = order
            # Устанавливаем клиента
            idx = self.client_combo.findData(customer_id)
            if idx >= 0:
                self.client_combo.setCurrentIndex(idx)
            # Статус
            idx = self.status_combo.findData(status_id)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
            # Адрес
            idx = self.address_combo.findData(point_id)
            if idx >= 0:
                self.address_combo.setCurrentIndex(idx)
            # Даты
            if order_date:
                self.order_date_edit.setDate(QDate.fromString(order_date, "yyyy-MM-dd"))
            if delivery_date:
                self.delivery_date_edit.setDate(QDate.fromString(delivery_date, "yyyy-MM-dd"))
            self.pickup_code_edit.setText(pickup_code or "")
        # Позиции
        products_dict = {pid: name for pid, name in get_all_products_for_combo()}
        for art, qty in items:
            name = products_dict.get(art, "")
            self.items.append([art, name, qty])
        self.refresh_items_table()

    def refresh_items_table(self):
        self.items_table.setRowCount(len(self.items))
        for row, (art, name, qty) in enumerate(self.items):
            self.items_table.setItem(row, 0, QTableWidgetItem(art))
            self.items_table.setItem(row, 1, QTableWidgetItem(name))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(qty)))
            del_btn = QPushButton("Удалить")
            del_btn.clicked.connect(lambda checked, r=row: self.delete_item_row(r))
            self.items_table.setCellWidget(row, 3, del_btn)
        self.items_table.resizeColumnsToContents()

    def delete_item_row(self, row):
        self.items.pop(row)
        self.refresh_items_table()

    def add_order_item(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор товара")
        dialog.setModal(True)
        d_layout = QVBoxLayout(dialog)

        combo = QComboBox()
        products = get_all_products_for_combo()
        for pid, name in products:
            combo.addItem(f"{pid} - {name}", pid)
        d_layout.addWidget(combo)

        d_layout.addWidget(QLabel("Количество:"))
        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setMaximum(9999)
        d_layout.addWidget(spin)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        d_layout.addWidget(btns)

        if dialog.exec_() == QDialog.Accepted:
            art = combo.currentData()
            qty = spin.value()
            name = next((n for pid, n in products if pid == art), "")
            self.items.append([art, name, qty])
            self.refresh_items_table()

    def validate(self):
        errors = []
        if self.client_combo.currentData() is None:
            errors.append("Выберите клиента.")
        if self.status_combo.currentData() is None:
            errors.append("Выберите статус.")
        if self.address_combo.currentData() is None:
            errors.append("Выберите пункт выдачи.")
        if not self.items:
            errors.append("Добавьте хотя бы одну позицию в заказ.")
        if self.is_new and self.order_id_edit.text().strip():
            try:
                new_id = int(self.order_id_edit.text())
                # уникальность проверится при сохранении
            except ValueError:
                errors.append("Номер заказа должен быть целым числом.")
        return errors

    def accept(self):
        errors = self.validate()
        if errors:
            QMessageBox.critical(self, "Ошибка", "\n".join(errors))
            return

        if self.is_new:
            if self.order_id_edit.text().strip():
                order_id = int(self.order_id_edit.text())
            else:
                order_id = get_next_order_id()
        else:
            order_id = self.order_id

        customer_id = self.client_combo.currentData()
        status_id = self.status_combo.currentData()
        point_id = self.address_combo.currentData()
        order_date = self.order_date_edit.date().toString("yyyy-MM-dd")
        delivery_date = self.delivery_date_edit.date().toString("yyyy-MM-dd")
        pickup_code = self.pickup_code_edit.text().strip()
        if not pickup_code:
            pickup_code = f"CODE{order_id}"

        items = [(art, qty) for art, _, qty in self.items]

        try:
            save_order(order_id, customer_id, status_id, point_id,
                       order_date, delivery_date, pickup_code, items, self.is_new)
            QMessageBox.information(self, "Успех", "Заказ сохранён.")
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить заказ:\n{str(e)}")