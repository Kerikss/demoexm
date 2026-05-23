import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # папка, где лежит config.py
DB_PATH = os.path.join(BASE_DIR, 'store.db')
RES_PATH = os.path.join(BASE_DIR, 'resources')
IMAGES_PATH = os.path.join(RES_PATH, 'images')
LOGO_PATH = os.path.join(RES_PATH, 'logo.png')
ICON_PATH = os.path.join(RES_PATH, 'icon.ico')
PLACEHOLDER_PATH = os.path.join(RES_PATH, 'picture.png')

os.makedirs(IMAGES_PATH, exist_ok=True)