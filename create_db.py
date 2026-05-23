import sqlite3
from config import DB_PATH

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Products (
            article TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            price REAL NOT NULL,
            supplier TEXT,
            manufacturer TEXT,
            category TEXT,
            discount INTEGER DEFAULT 0,
            stock_quantity INTEGER DEFAULT 0,
            description TEXT,
            photo TEXT
        );

        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS PickupPoints (
            point_id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS OrderStatuses (
            status_id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            pickup_point_id INTEGER NOT NULL,
            order_date TEXT,
            delivery_date TEXT,
            pickup_code TEXT,
            status_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (pickup_point_id) REFERENCES PickupPoints(point_id) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (status_id) REFERENCES OrderStatuses(status_id) ON UPDATE CASCADE ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS OrderItems (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_article TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_article) REFERENCES Products(article) ON UPDATE CASCADE ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_orders_user ON Orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON Orders(status_id);
        CREATE INDEX IF NOT EXISTS idx_orderitems_order ON OrderItems(order_id);
        CREATE INDEX IF NOT EXISTS idx_orderitems_product ON OrderItems(product_article);
    ''')

    conn.commit()
    conn.close()
    print(f"База данных создана: {DB_PATH}")

if __name__ == '__main__':
    create_database()