import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

# ------------------- ПОЛЬЗОВАТЕЛИ -------------------
def get_user(login, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.RoleName, u.LastName, u.FirstName, u.MiddleName
        FROM UserAccounts ua
        JOIN Users u ON ua.UserID = u.UserID
        JOIN Roles r ON ua.RoleID = r.RoleID
        WHERE ua.Login = ? AND ua.Password = ?
    """, (login, password))
    row = cur.fetchone()
    conn.close()
    if row:
        role = row[0]
        full_name = f"{row[1]} {row[2]} {row[3] or ''}".strip()
        return role, full_name
    return None

# ------------------- ТОВАРЫ -------------------
def get_products(search_text="", supplier_filter="", sort_order=""):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            p.ProductID,
            p.ProductName,
            c.CategoryName,
            p.Description,
            m.ManufacturerName,
            s.SupplierName,
            p.Price,
            p.Unit,
            p.StockQuantity,
            p.Discount,
            p.Photo
        FROM Products p
        JOIN Suppliers s ON p.SupplierID = s.SupplierID
        JOIN Manufacturers m ON p.ManufacturerID = m.ManufacturerID
        JOIN Categories c ON p.CategoryID = c.CategoryID
        WHERE 1=1
    """
    params = []
    if search_text:
        query += """ AND (
            p.ProductName LIKE ? OR c.CategoryName LIKE ? OR p.Description LIKE ? OR
            m.ManufacturerName LIKE ? OR s.SupplierName LIKE ? OR p.ProductID LIKE ?
        )"""
        like = f"%{search_text}%"
        params.extend([like, like, like, like, like, like])
    if supplier_filter and supplier_filter != "Все поставщики":
        query += " AND s.SupplierName = ?"
        params.append(supplier_filter)
    if sort_order in ("ASC", "DESC"):
        query += f" ORDER BY p.StockQuantity {sort_order}"
    else:
        query += " ORDER BY p.ProductName"
    cur.execute(query, params)
    products = cur.fetchall()
    conn.close()
    return products

def get_all_suppliers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SupplierName FROM Suppliers ORDER BY SupplierName")
    return [row[0] for row in cur.fetchall()]

def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT CategoryName FROM Categories ORDER BY CategoryName")
    return [row[0] for row in cur.fetchall()]

def get_all_manufacturers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT ManufacturerName FROM Manufacturers ORDER BY ManufacturerName")
    return [row[0] for row in cur.fetchall()]

def get_supplier_id_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SupplierID FROM Suppliers WHERE SupplierName=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_manufacturer_id_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT ManufacturerID FROM Manufacturers WHERE ManufacturerName=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_category_id_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT CategoryID FROM Categories WHERE CategoryName=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def product_exists_in_orders(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM OrderItems WHERE ProductArticle=?", (product_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Photo FROM Products WHERE ProductID=?", (product_id,))
    row = cur.fetchone()
    if row and row[0]:
        from config import IMAGES_PATH
        import os
        photo_path = os.path.join(IMAGES_PATH, row[0])
        cur.execute("SELECT COUNT(*) FROM Products WHERE Photo=? AND ProductID!=?", (row[0], product_id))
        if cur.fetchone()[0] == 0 and os.path.exists(photo_path):
            os.remove(photo_path)
    cur.execute("DELETE FROM Products WHERE ProductID=?", (product_id,))
    conn.commit()
    conn.close()

def save_product(product_id, name, unit, price, supplier_name, manufacturer_name, category_name,
                 discount, stock_quantity, description, photo_filename, is_new):
    conn = get_connection()
    cur = conn.cursor()
    supplier_id = get_supplier_id_by_name(supplier_name)
    if supplier_id is None:
        cur.execute("INSERT INTO Suppliers (SupplierName) VALUES (?)", (supplier_name,))
        supplier_id = cur.lastrowid
    manufacturer_id = get_manufacturer_id_by_name(manufacturer_name)
    if manufacturer_id is None:
        cur.execute("INSERT INTO Manufacturers (ManufacturerName) VALUES (?)", (manufacturer_name,))
        manufacturer_id = cur.lastrowid
    category_id = get_category_id_by_name(category_name)
    if category_id is None:
        cur.execute("INSERT INTO Categories (CategoryName) VALUES (?)", (category_name,))
        category_id = cur.lastrowid

    if is_new:
        cur.execute("""
            INSERT INTO Products 
            (ProductID, ProductName, Unit, Price, SupplierID, ManufacturerID, CategoryID,
             Discount, StockQuantity, Description, Photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, name, unit, price, supplier_id, manufacturer_id, category_id,
              discount, stock_quantity, description, photo_filename))
    else:
        cur.execute("""
            UPDATE Products
            SET ProductName=?, Unit=?, Price=?, SupplierID=?, ManufacturerID=?, CategoryID=?,
                Discount=?, StockQuantity=?, Description=?, Photo=?
            WHERE ProductID=?
        """, (name, unit, price, supplier_id, manufacturer_id, category_id,
              discount, stock_quantity, description, photo_filename, product_id))
    conn.commit()
    conn.close()

# ------------------- ЗАКАЗЫ -------------------
def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            o.OrderID,
            u.LastName,
            u.FirstName,
            u.MiddleName,
            os.StatusName,
            p.PostalCode || ', ' || p.City || ', ул. ' || p.Street || ', ' || p.HouseNumber AS Address,
            o.OrderDate,
            o.DeliveryDate,
            o.PickupCode
        FROM Orders o
        JOIN Users u ON o.CustomerID = u.UserID
        JOIN OrderStatuses os ON o.StatusID = os.StatusID
        JOIN PickupPoints p ON o.PickupPointID = p.PointID
        ORDER BY o.OrderID
    """)
    orders = cur.fetchall()  # (OrderID, LastName, FirstName, MiddleName, StatusName, Address, OrderDate, DeliveryDate, PickupCode)
    conn.close()
    return orders

def get_order_by_id(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT CustomerID, StatusID, PickupPointID, OrderDate, DeliveryDate, PickupCode
        FROM Orders WHERE OrderID=?
    """, (order_id,))
    order = cur.fetchone()
    items = []
    if order:
        cur.execute("SELECT ProductArticle, Quantity FROM OrderItems WHERE OrderID=?", (order_id,))
        items = cur.fetchall()
    conn.close()
    return order, items

def save_order(order_id, customer_id, status_id, point_id, order_date, delivery_date, pickup_code, items, is_new):
    conn = get_connection()
    cur = conn.cursor()
    if is_new:
        cur.execute("""
            INSERT INTO Orders 
            (OrderID, CustomerID, PickupPointID, OrderDate, DeliveryDate, PickupCode, StatusID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (order_id, customer_id, point_id, order_date, delivery_date, pickup_code, status_id))
    else:
        cur.execute("""
            UPDATE Orders
            SET CustomerID=?, PickupPointID=?, OrderDate=?, DeliveryDate=?, PickupCode=?, StatusID=?
            WHERE OrderID=?
        """, (customer_id, point_id, order_date, delivery_date, pickup_code, status_id, order_id))
        cur.execute("DELETE FROM OrderItems WHERE OrderID=?", (order_id,))
    for art, qty in items:
        cur.execute("INSERT INTO OrderItems (OrderID, ProductArticle, Quantity) VALUES (?,?,?)",
                    (order_id, art, qty))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM OrderItems WHERE OrderID=?", (order_id,))
    cur.execute("DELETE FROM Orders WHERE OrderID=?", (order_id,))
    conn.commit()
    conn.close()

def get_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.UserID, u.LastName || ' ' || u.FirstName || ' ' || COALESCE(u.MiddleName, '') AS FullName
        FROM Users u
        JOIN UserAccounts ua ON u.UserID = ua.UserID
        WHERE ua.RoleID IN (SELECT RoleID FROM Roles WHERE RoleName IN ('Авторизированный клиент', 'Менеджер'))
    """)
    clients = cur.fetchall()
    conn.close()
    return clients

def get_order_statuses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT StatusID, StatusName FROM OrderStatuses")
    return cur.fetchall()

def get_pickup_points():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT PointID, PostalCode || ', ' || City || ', ул. ' || Street || ', ' || HouseNumber AS Address
        FROM PickupPoints
    """)
    points = cur.fetchall()
    conn.close()
    return points

def get_next_order_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(OrderID) FROM Orders")
    max_id = cur.fetchone()[0]
    conn.close()
    return (max_id or 0) + 1

def get_all_products_for_combo():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT ProductID, ProductName FROM Products ORDER BY ProductName")
    products = cur.fetchall()
    conn.close()
    return products