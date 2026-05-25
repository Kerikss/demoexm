import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QComboBox, QMessageBox)
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtCore import Qt
from config import LOGO_PATH, ICON_PATH, IMAGES_PATH, PLACEHOLDER_PATH
from database import (get_products, get_all_suppliers, delete_product,
                      product_exists_in_orders)
from dialogs.product_edit_dialog import ProductEditDialog
from windows.orders_window import OrdersWindow

class ProductWindow(QMainWindow):
    def __init__(self, role, full_name=None):
        super().__init__()
        self.role = role
        self.full_name = full_name
        self.current_search = ""
        self.current_supplier = "Все поставщики"
        self.current_sort = ""
        self.edit_dialog = None
        self.setWindowTitle("Обувь - Каталог товаров")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Times New Roman';")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

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

        # Кнопка "Заказы" для менеджера и админа
        if self.role in ('Менеджер', 'Администратор'):
            orders_btn = QPushButton("Заказы")
            orders_btn.setStyleSheet("background-color: #7FFF00; padding: 5px;")
            orders_btn.clicked.connect(self.show_orders)
            top_bar.addWidget(orders_btn)

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet("background-color: #7FFF00; padding: 5px;")
        back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(back_btn)

        logout_btn = QPushButton("Выйти")
        logout_btn.setStyleSheet("background-color: #7FFF00; padding: 5px;")
        logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(logout_btn)

        main_layout.addLayout(top_bar)

        # Панель поиска/фильтрации (только менеджер/админ)
        if self.role in ('Менеджер', 'Администратор'):
            control_panel = QHBoxLayout()
            control_panel.addWidget(QLabel("Поиск:"))
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Введите текст...")
            self.search_edit.textChanged.connect(self.on_search_changed)
            control_panel.addWidget(self.search_edit)

            control_panel.addWidget(QLabel("Поставщик:"))
            self.supplier_combo = QComboBox()
            self.supplier_combo.addItem("Все поставщики")
            self.supplier_combo.addItems(get_all_suppliers())
            self.supplier_combo.currentTextChanged.connect(self.on_filter_changed)
            control_panel.addWidget(self.supplier_combo)

            control_panel.addWidget(QLabel("Сортировка по кол-ву:"))
            self.sort_combo = QComboBox()
            self.sort_combo.addItem("Без сортировки", "")
            self.sort_combo.addItem("По возрастанию", "ASC")
            self.sort_combo.addItem("По убыванию", "DESC")
            self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
            control_panel.addWidget(self.sort_combo)

            main_layout.addLayout(control_panel)

        # Кнопка "Добавить товар" для админа
        if self.role == 'Администратор':
            admin_btns = QHBoxLayout()
            self.add_btn = QPushButton("Добавить товар")
            self.add_btn.setStyleSheet("background-color: #00FA9A; padding: 5px;")
            self.add_btn.clicked.connect(self.add_product)
            admin_btns.addWidget(self.add_btn)
            admin_btns.addStretch()
            main_layout.addLayout(admin_btns)

        # Таблица товаров
        self.table = QTableWidget()
        col_count = 11
        headers = ["Фото", "Артикул", "Наименование", "Категория", "Описание",
                   "Производитель", "Поставщик", "Цена", "Ед. изм.",
                   "Кол-во", "Скидка %"]
        if self.role == 'Администратор':
            headers.append("Действия")
            col_count = 12
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        if self.role == 'Администратор':
            self.table.doubleClicked.connect(self.edit_product_from_table)

        main_layout.addWidget(self.table)
        self.load_products()

    def go_back(self):
        self.close()
        from windows.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def logout(self):
        self.close()
        from windows.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def show_orders(self):
        self.orders_window = OrdersWindow(self.role, self.full_name)
        self.orders_window.show()

    def on_search_changed(self, text):
        self.current_search = text
        self.apply_filters()

    def on_filter_changed(self, supplier):
        self.current_supplier = supplier
        self.apply_filters()

    def on_sort_changed(self):
        self.current_sort = self.sort_combo.currentData()
        self.apply_filters()

    def apply_filters(self):
        self.load_products()

    def load_products(self):
        try:
            products = get_products(
                search_text=self.current_search,
                supplier_filter=self.current_supplier,
                sort_order=self.current_sort
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить товары:\n{str(e)}")
            return

        self.table.setRowCount(len(products))
        for row, prod in enumerate(products):
            # prod: (ProductID, ProductName, CategoryName, Description, ManufacturerName,
            #        SupplierName, Price, Unit, StockQuantity, Discount, Photo)
            product_id, name, category, description, manufacturer, supplier, \
            price, unit, stock, discount, photo = prod

            # Фото
            photo_path = os.path.join(IMAGES_PATH, photo) if photo else None
            if photo_path and os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
            else:
                pixmap = QPixmap(PLACEHOLDER_PATH)
            icon = QIcon(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            item_photo = QTableWidgetItem()
            item_photo.setIcon(icon)
            self.table.setItem(row, 0, item_photo)

            self.table.setItem(row, 1, QTableWidgetItem(product_id))       # Артикул
            self.table.setItem(row, 2, QTableWidgetItem(name))             # Наименование
            self.table.setItem(row, 3, QTableWidgetItem(category))         # Категория
            short_desc = description[:80] + "..." if description and len(description) > 80 else description
            self.table.setItem(row, 4, QTableWidgetItem(short_desc or "")) # Описание
            self.table.setItem(row, 5, QTableWidgetItem(manufacturer or ""))
            self.table.setItem(row, 6, QTableWidgetItem(supplier or ""))

            # Цена со скидкой (через QLabel для HTML)
            old_price = float(price)
            if discount and discount > 0:
                new_price = round(old_price * (100 - discount) / 100, 2)
                price_text = f'<span style="text-decoration: line-through; color: red;">{old_price:.2f}</span> <b>{new_price:.2f}</b>'
            else:
                price_text = f'{old_price:.2f}'
            label_price = QLabel(price_text)
            label_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label_price.setTextFormat(Qt.RichText)
            self.table.setCellWidget(row, 7, label_price)

            self.table.setItem(row, 8, QTableWidgetItem(unit))
            self.table.setItem(row, 9, QTableWidgetItem(str(stock)))
            self.table.setItem(row, 10, QTableWidgetItem(f"{discount}%" if discount else "0%"))

            # Подсветка строк
            if stock == 0:
                bg_color = QColor(173, 216, 230)  # голубой
            elif discount and discount > 15:
                bg_color = QColor(46, 139, 87)    # #2E8B57
            else:
                bg_color = None
            if bg_color:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(bg_color)

            # Кнопки действий для админа
            if self.role == 'Администратор':
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 25)
                edit_btn.setToolTip("Редактировать")
                edit_btn.clicked.connect(lambda checked, pid=product_id: self.edit_product(pid))
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(30, 25)
                delete_btn.setToolTip("Удалить")
                delete_btn.clicked.connect(lambda checked, pid=product_id: self.delete_product(pid))
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.addStretch()
                self.table.setCellWidget(row, 11, btn_widget)

        self.table.resizeColumnsToContents()

    def add_product(self):
        if self.edit_dialog and self.edit_dialog.isVisible():
            QMessageBox.warning(self, "Внимание", "Окно редактирования уже открыто.")
            return
        self.edit_dialog = ProductEditDialog(self, product_id=None)
        self.edit_dialog.finished.connect(self.on_edit_finished)
        self.edit_dialog.show()

    def edit_product(self, product_id):
        if self.edit_dialog and self.edit_dialog.isVisible():
            QMessageBox.warning(self, "Внимание", "Окно редактирования уже открыто.")
            return
        self.edit_dialog = ProductEditDialog(self, product_id=product_id)
        self.edit_dialog.finished.connect(self.on_edit_finished)
        self.edit_dialog.show()

    def edit_product_from_table(self, index):
        row = index.row()
        product_id_item = self.table.item(row, 1)
        if product_id_item:
            self.edit_product(product_id_item.text())

    def delete_product(self, product_id):
        if product_exists_in_orders(product_id):
            QMessageBox.warning(self, "Невозможно удалить",
                                f"Товар с артикулом {product_id} присутствует в заказах.\nУдаление запрещено.")
            return
        reply = QMessageBox.question(self, "Подтверждение удаления",
                                     f"Вы действительно хотите удалить товар {product_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                delete_product(product_id)
                QMessageBox.information(self, "Успех", "Товар удалён.")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить товар:\n{str(e)}")

    def on_edit_finished(self):
        self.edit_dialog = None
        self.load_products()