import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sales_forecasting.db"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_connection():
    return get_db()


def _tables(db):
    return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _columns(db, table):
    return {r[1] for r in db.execute(f"PRAGMA table_info({table})")}


def _add_column(db, table, column, definition):
    if column not in _columns(db, table):
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _rename_if_legacy(db, table, required_columns, legacy_name):
    """Rename an incompatible old table instead of destroying its data."""
    if table in _tables(db):
        cols = _columns(db, table)
        if not set(required_columns).issubset(cols):
            if legacy_name not in _tables(db):
                db.execute(f"ALTER TABLE {table} RENAME TO {legacy_name}")
            else:
                db.execute(f"DROP TABLE {table}")
            return True
    return False


def initialize_database():
    """Initialize/migrate the SalesPro database without deleting old data."""
    db = get_db()
    tables = _tables(db)

    # ---------------- USERS ----------------
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL DEFAULT '',
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _add_column(db, "users", "name", "TEXT")
    _add_column(db, "users", "active", "INTEGER NOT NULL DEFAULT 1")
    db.execute("UPDATE users SET name = COALESCE(NULLIF(name,''), full_name)")
    db.execute("UPDATE users SET full_name = COALESCE(NULLIF(full_name,''), name)")
    db.execute("UPDATE users SET active = 1 WHERE active IS NULL")

    # ---------------- CATEGORIES ----------------
    db.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # ---------------- SUPPLIERS ----------------
    db.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------- PRODUCTS ----------------
    # Old project table had required columns (name/code/quantity) that conflict
    # with the current Flask API. Preserve it, then create the API-compatible table.
    if _rename_if_legacy(
        db, "products",
        ["id", "owner_id", "product_name", "category", "price", "stock_quantity"],
        "products_legacy"
    ):
        db.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL DEFAULT 0,
                stock_quantity INTEGER NOT NULL DEFAULT 0
            )
        """)
        legacy_cols = _columns(db, "products_legacy")
        if "user_id" in legacy_cols:
            db.execute("""
                INSERT INTO products (owner_id, product_name, category, price, stock_quantity)
                SELECT user_id, name, category, COALESCE(price,0), COALESCE(quantity,0)
                FROM products_legacy
            """)
    elif "products" not in _tables(db):
        db.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL DEFAULT 0,
                stock_quantity INTEGER NOT NULL DEFAULT 0
            )
        """)

    # ---------------- CUSTOMERS ----------------
    if _rename_if_legacy(
        db, "customers",
        ["id", "owner_id", "customer_name", "phone", "email", "address"],
        "customers_legacy"
    ):
        db.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)
        legacy_cols = _columns(db, "customers_legacy")
        if "user_id" in legacy_cols:
            db.execute("""
                INSERT INTO customers (owner_id, customer_name, phone, email, address)
                SELECT user_id, name, phone, email, address
                FROM customers_legacy
            """)
    elif "customers" not in _tables(db):
        db.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

    _add_column(db, "customers", "customer_code", "TEXT")

    # ---------------- SALES ----------------
    if _rename_if_legacy(
        db, "sales",
        ["id", "owner_id", "invoice_no", "product_name", "customer_name", "quantity", "price", "discount", "tax", "sale_date", "total_amount"],
        "sales_legacy"
    ):
        db.execute("""
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                invoice_no TEXT NOT NULL,
                product_name TEXT NOT NULL,
                customer_name TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL DEFAULT 0,
                discount REAL NOT NULL DEFAULT 0,
                tax REAL NOT NULL DEFAULT 0,
                sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL DEFAULT 0
            )
        """)
        legacy_cols = _columns(db, "sales_legacy")
        if "user_id" in legacy_cols:
            db.execute("""
                INSERT INTO sales
                (owner_id, invoice_no, product_name, customer_name, quantity, price, discount, tax, sale_date, total_amount)
                SELECT
                    user_id,
                    'INV-' || id,
                    COALESCE(product_name, ''),
                    customer_name,
                    COALESCE(quantity,1),
                    COALESCE(price,0),
                    0,
                    0,
                    sale_date,
                    COALESCE(total_amount,0)
                FROM sales_legacy
            """)
    elif "sales" not in _tables(db):
        db.execute("""
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                invoice_no TEXT NOT NULL,
                product_name TEXT NOT NULL,
                customer_name TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL DEFAULT 0,
                discount REAL NOT NULL DEFAULT 0,
                tax REAL NOT NULL DEFAULT 0,
                sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL DEFAULT 0
            )
        """)

    # ---------------- PURCHASES ----------------
    db.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            supplier_name TEXT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            purchase_price REAL NOT NULL DEFAULT 0,
            purchase_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------- SALES RETURNS ----------------
    db.execute("""
        CREATE TABLE IF NOT EXISTS sales_returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            invoice_no TEXT NOT NULL,
            product_name TEXT NOT NULL,
            return_quantity INTEGER NOT NULL DEFAULT 0,
            reason TEXT,
            refund_amount REAL NOT NULL DEFAULT 0,
            return_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    db.close()


def authenticate_user(email, password):
    db = get_db()
    try:
        user = db.execute(
            "SELECT id, name, full_name, email, password, role, active FROM users WHERE LOWER(email)=LOWER(?)",
            (email.strip(),)
        ).fetchone()
    finally:
        db.close()

    if not user or not user["active"]:
        return None

    try:
        valid = check_password_hash(user["password"], password)
    except Exception:
        valid = user["password"] == password

    if not valid:
        return None

    return {
        "id": user["id"],
        "name": user["name"] or user["full_name"],
        "full_name": user["full_name"] or user["name"],
        "email": user["email"],
        "role": user["role"],
        "active": user["active"],
    }


def register_user(full_name, email, password):
    db = get_db()
    try:
        if db.execute("SELECT id FROM users WHERE LOWER(email)=LOWER(?)", (email.strip(),)).fetchone():
            return False, "Email already registered"

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (full_name, name, email, password, role, active) VALUES (?, ?, ?, ?, 'user', 1)",
            (full_name.strip(), full_name.strip(), email.strip().lower(), password_hash)
        )
        db.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        db.rollback()
        return False, "Email already registered"
    finally:
        db.close()


def reset_user_password(user_name, email, new_password):
    db = get_db()
    try:
        password_hash = generate_password_hash(new_password)
        cur = db.execute(
            "UPDATE users SET password=? WHERE LOWER(email)=LOWER(?) AND name=?",
            (password_hash, email.strip(), user_name.strip())
        )
        if cur.rowcount == 0:
            return False, "No account was found with this email address."
        db.commit()
        return True, "Password reset successfully. You can now sign in."
    except sqlite3.Error:
        db.rollback()
        return False, "Unable to reset the password. Please try again."
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database ready: {DB_PATH}")
