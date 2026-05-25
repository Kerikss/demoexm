import os
from PIL import Image
from PyQt5.QtGui import QPixmap
from config import IMAGES_PATH, PLACEHOLDER_PATH

def save_photo(file_path):
    if not file_path:
        return None
    img = Image.open(file_path)
    img.thumbnail((300, 200))
    base_name = os.path.basename(file_path).replace(" ", "_")
    dest_path = os.path.join(IMAGES_PATH, base_name)
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(base_name)
        dest_path = os.path.join(IMAGES_PATH, f"{name}_{counter}{ext}")
        counter += 1
    img.save(dest_path)
    return os.path.basename(dest_path)

def get_pixmap(photo_filename):
    if photo_filename:
        path = os.path.join(IMAGES_PATH, photo_filename)
        if os.path.exists(path):
            return QPixmap(path)
    return QPixmap(PLACEHOLDER_PATH)

def validate_product_input(article, name, price_str, discount_str, stock_str, is_new, existing_articles=None):
    errors = []
    if not article.strip():
        errors.append("Артикул не может быть пустым.")
    if is_new and existing_articles and article in existing_articles:
        errors.append("Товар с таким артикулом уже существует.")
    if not name.strip():
        errors.append("Наименование товара обязательно.")
    try:
        price = float(price_str.replace(",", "."))
        if price < 0:
            errors.append("Цена не может быть отрицательной.")
    except:
        errors.append("Цена должна быть числом (возможно, дробным).")
    try:
        discount = int(discount_str)
        if discount < 0 or discount > 100:
            errors.append("Скидка должна быть от 0 до 100.")
    except:
        errors.append("Скидка должна быть целым числом.")
    try:
        stock = int(stock_str)
        if stock < 0:
            errors.append("Количество не может быть отрицательным.")
    except:
        errors.append("Количество должно быть целым числом.")
    return errors