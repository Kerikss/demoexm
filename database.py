import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

# ------------------- ПОЛЬЗОВАТЕЛИ -------------------
def get_user(login, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, full_name FROM Users WHERE login=? AND password=?", (login, password))
    user = cur.fetchone()
    conn.close()
    return user

# ------------------- ТОВАРЫ -------------------
def get_products(search_text="", supplier_filter="", sort_order=""):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT article, name, category, description, manufacturer,
               supplier, price, unit, stock_quantity, discount, photo
        FROM Products WHERE 1=1
    """
    params = []
    if search_text:
        query += """ AND (name LIKE ? OR category LIKE ? OR description LIKE ? OR
                         manufacturer LIKE ? OR supplier LIKE ? OR article LIKE ?)"""
        like = f"%{search_text}%"
        params.extend([like, like, like, like, like, like])
    if supplier_filter and supplier_filter != "Все поставщики":
        query += " AND supplier = ?"
        params.append(supplier_filter)
    if sort_order in ("ASC", "DESC"):
        query += f" ORDER BY stock_quantity {sort_order}"
    else:
        query += " ORDER BY name"
    cur.execute(query, params)
    products = cur.fetchall()
    conn.close()
    return products

def get_all_suppliers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT supplier FROM Products WHERE supplier IS NOT NULL ORDER BY supplier")
    suppliers = [row[0] for row in cur.fetchall()]
    conn.close()
    return suppliers

def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM Products WHERE category IS NOT NULL ORDER BY category")
    categories = [row[0] for row in cur.fetchall()]
    conn.close()
    return categories

def get_all_manufacturers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT manufacturer FROM Products WHERE manufacturer IS NOT NULL ORDER BY manufacturer")
    manufacturers = [row[0] for row in cur.fetchall()]
    conn.close()
    return manufacturers

def product_exists_in_orders(article):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM OrderItems WHERE product_article=?", (article,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

def delete_product(article):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT photo FROM Products WHERE article=?", (article,))
    row = cur.fetchone()
    if row and row[0]:
        from config import IMAGES_PATH
        import os
        photo_path = os.path.join(IMAGES_PATH, row[0])
        cur.execute("SELECT COUNT(*) FROM Products WHERE photo=? AND article!=?", (row[0], article))
        if cur.fetchone()[0] == 0 and os.path.exists(photo_path):
            os.remove(photo_path)
    cur.execute("DELETE FROM Products WHERE article=?", (article,))
    conn.commit()
    conn.close()

def save_product(article, name, unit, price, supplier, manufacturer, category,
                 discount, stock_quantity, description, photo_filename, is_new):
    conn = get_connection()
    cur = conn.cursor()
    if is_new:
        cur.execute("""
            INSERT INTO Products
            (article, name, unit, price, supplier, manufacturer, category,
             discount, stock_quantity, description, photo)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (article, name, unit, price, supplier, manufacturer, category,
              discount, stock_quantity, description, photo_filename))
    else:
        cur.execute("""
            UPDATE Products
            SET name=?, unit=?, price=?, supplier=?, manufacturer=?,
                category=?, discount=?, stock_quantity=?, description=?, photo=?
            WHERE article=?
        """, (name, unit, price, supplier, manufacturer, category,
              discount, stock_quantity, description, photo_filename, article))
    conn.commit()
    conn.close()

# ------------------- ЗАКАЗЫ -------------------
def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.order_id, u.full_name, s.status_name, p.address,
               o.order_date, o.delivery_date, o.pickup_code
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id
        JOIN OrderStatuses s ON o.status_id = s.status_id
        JOIN PickupPoints p ON o.pickup_point_id = p.point_id
        ORDER BY o.order_id
    """)
    orders = cur.fetchall()
    conn.close()
    return orders

def get_order_by_id(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, status_id, pickup_point_id, order_date, delivery_date, pickup_code
        FROM Orders WHERE order_id=?
    """, (order_id,))
    order = cur.fetchone()
    items = []
    if order:
        cur.execute("""
            SELECT product_article, quantity
            FROM OrderItems WHERE order_id=?
        """, (order_id,))
        items = cur.fetchall()
    conn.close()
    return order, items

def save_order(order_id, user_id, status_id, point_id, order_date, delivery_date, pickup_code, items, is_new):
    conn = get_connection()
    cur = conn.cursor()
    if is_new:
        cur.execute("""
            INSERT INTO Orders (order_id, user_id, pickup_point_id, order_date, delivery_date, pickup_code, status_id)
            VALUES (?,?,?,?,?,?,?)
        """, (order_id, user_id, point_id, order_date, delivery_date, pickup_code, status_id))
    else:
        cur.execute("""
            UPDATE Orders
            SET user_id=?, pickup_point_id=?, order_date=?, delivery_date=?, pickup_code=?, status_id=?
            WHERE order_id=?
        """, (user_id, point_id, order_date, delivery_date, pickup_code, status_id, order_id))
        cur.execute("DELETE FROM OrderItems WHERE order_id=?", (order_id,))
    for art, qty in items:
        cur.execute("INSERT INTO OrderItems (order_id, product_article, quantity) VALUES (?,?,?)",
                    (order_id, art, qty))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM OrderItems WHERE order_id=?", (order_id,))
    cur.execute("DELETE FROM Orders WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()

def get_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, full_name FROM Users WHERE role IN ('Авторизированный клиент', 'Менеджер')")
    clients = cur.fetchall()
    conn.close()
    return clients

def get_order_statuses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status_id, status_name FROM OrderStatuses")
    statuses = cur.fetchall()
    conn.close()
    return statuses

def get_pickup_points():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT point_id, address FROM PickupPoints")
    points = cur.fetchall()
    conn.close()
    return points

def get_next_order_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(order_id) FROM Orders")
    max_id = cur.fetchone()[0]
    conn.close()
    return (max_id or 0) + 1

def get_all_products_for_combo():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT article, name FROM Products ORDER BY name")
    products = cur.fetchall()
    conn.close()
    return products