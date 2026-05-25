import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QComboBox, QPushButton, QLabel, QHBoxLayout,
                             QMessageBox, QFileDialog, QDialogButtonBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from database import (save_product, get_all_categories, get_all_manufacturers,
                      get_all_suppliers, get_products)
from utils.helpers import save_photo, validate_product_input

class ProductEditDialog(QDialog):
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.parent_window = parent
        self.product_id = product_id
        self.is_new = (product_id is None)
        self.photo_filename = None
        self.setWindowTitle("Добавление товара" if self.is_new else "Редактирование товара")
        self.setModal(True)
        self.setMinimumSize(500, 600)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Артикул (ProductID)
        self.article_edit = QLineEdit()
        if not self.is_new:
            self.article_edit.setReadOnly(True)
        form.addRow("Артикул:", self.article_edit)

        self.name_edit = QLineEdit()
        form.addRow("Наименование:", self.name_edit)

        self.unit_edit = QLineEdit()
        self.unit_edit.setText("шт.")
        form.addRow("Ед. измерения:", self.unit_edit)

        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("0.00")
        form.addRow("Цена:", self.price_edit)

        # Поставщик (выпадающий список с возможностью добавления)
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItems(get_all_suppliers())
        self.supplier_combo.setEditable(True)
        form.addRow("Поставщик:", self.supplier_combo)

        # Производитель
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItems(get_all_manufacturers())
        self.manufacturer_combo.setEditable(True)
        form.addRow("Производитель:", self.manufacturer_combo)

        # Категория
        self.category_combo = QComboBox()
        self.category_combo.addItems(get_all_categories())
        self.category_combo.setEditable(True)
        form.addRow("Категория:", self.category_combo)

        self.discount_edit = QLineEdit()
        self.discount_edit.setPlaceholderText("0")
        form.addRow("Скидка (%):", self.discount_edit)

        self.stock_edit = QLineEdit()
        self.stock_edit.setPlaceholderText("0")
        form.addRow("Кол-во на складе:", self.stock_edit)

        self.description_edit = QLineEdit()
        form.addRow("Описание:", self.description_edit)

        # Фото
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 100)
        self.photo_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setText("Нет фото")
        self.photo_button = QPushButton("Выбрать фото")
        self.photo_button.clicked.connect(self.choose_photo)
        photo_layout.addWidget(self.photo_label)
        photo_layout.addWidget(self.photo_button)
        form.addRow("Фото:", photo_layout)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if not self.is_new:
            self.load_product_data()

    def load_product_data(self):
        from database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.ProductID, p.ProductName, p.Unit, p.Price,
                   s.SupplierName, m.ManufacturerName, c.CategoryName,
                   p.Discount, p.StockQuantity, p.Description, p.Photo
            FROM Products p
            JOIN Suppliers s ON p.SupplierID = s.SupplierID
            JOIN Manufacturers m ON p.ManufacturerID = m.ManufacturerID
            JOIN Categories c ON p.CategoryID = c.CategoryID
            WHERE p.ProductID=?
        """, (self.product_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            self.article_edit.setText(row[0])
            self.name_edit.setText(row[1] or "")
            self.unit_edit.setText(row[2] or "шт.")
            self.price_edit.setText(str(row[3]) if row[3] is not None else "")
            # Поставщик
            idx = self.supplier_combo.findText(row[4])
            if idx >= 0:
                self.supplier_combo.setCurrentIndex(idx)
            else:
                self.supplier_combo.setEditText(row[4])
            # Производитель
            idx = self.manufacturer_combo.findText(row[5])
            if idx >= 0:
                self.manufacturer_combo.setCurrentIndex(idx)
            else:
                self.manufacturer_combo.setEditText(row[5])
            # Категория
            idx = self.category_combo.findText(row[6])
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            else:
                self.category_combo.setEditText(row[6])
            self.discount_edit.setText(str(row[7]) if row[7] is not None else "0")
            self.stock_edit.setText(str(row[8]) if row[8] is not None else "0")
            self.description_edit.setText(row[9] or "")
            if row[10]:
                from config import IMAGES_PATH
                photo_path = os.path.join(IMAGES_PATH, row[10])
                if os.path.exists(photo_path):
                    pixmap = QPixmap(photo_path)
                    scaled = pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.photo_label.setPixmap(scaled)
                    self.photo_filename = row[10]
                else:
                    self.photo_label.setText("Файл не найден")
            else:
                self.photo_label.setText("Нет фото")

    def choose_photo(self):
        from config import IMAGES_PATH
        from utils.helpers import save_photo
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                filename = save_photo(file_path)
                if filename:
                    self.photo_filename = filename
                    pixmap = QPixmap(os.path.join(IMAGES_PATH, filename))
                    scaled = pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.photo_label.setPixmap(scaled)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить фото.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить фото:\n{str(e)}")

    def validate(self):
        existing = set()
        if self.is_new:
            products = get_products()
            for p in products:
                existing.add(p[0])
        errors = validate_product_input(
            self.article_edit.text(),
            self.name_edit.text(),
            self.price_edit.text(),
            self.discount_edit.text(),
            self.stock_edit.text(),
            self.is_new,
            existing
        )
        return errors

    def accept(self):
        errors = self.validate()
        if errors:
            QMessageBox.critical(self, "Ошибка ввода", "\n".join(errors))
            return

        product_id = self.article_edit.text().strip()
        name = self.name_edit.text().strip()
        unit = self.unit_edit.text().strip() or "шт."
        price = float(self.price_edit.text().replace(",", "."))
        supplier = self.supplier_combo.currentText().strip()
        manufacturer = self.manufacturer_combo.currentText().strip()
        category = self.category_combo.currentText().strip()
        discount = int(self.discount_edit.text())
        stock = int(self.stock_edit.text())
        description = self.description_edit.text().strip()

        # Если при редактировании фото не меняли, оставляем старое
        if self.photo_filename is None and not self.is_new:
            from database import get_connection
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT Photo FROM Products WHERE ProductID=?", (product_id,))
            row = cur.fetchone()
            if row and row[0]:
                self.photo_filename = row[0]
            conn.close()

        try:
            save_product(product_id, name, unit, price, supplier, manufacturer, category,
                         discount, stock, description, self.photo_filename, self.is_new)
            QMessageBox.information(self, "Успех", "Товар сохранён.")
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить товар:\n{str(e)}")