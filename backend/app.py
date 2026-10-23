import os
import csv
import io
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, initialize_database


app = Flask(__name__)

# Development CORS.
# For production, replace "*" with your deployed frontend URL.
CORS(app, resources={r"/api/*": {"origins": "*"}})

SECRET_KEY = os.environ.get(
    "SALESPRO_SECRET_KEY",
    "change-this-secret-before-deployment"
)

app.config["SECRET_KEY"] = SECRET_KEY


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

initialize_database()


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def row_to_dict(row):
    if row is None:
        return None

    return dict(row)


def rows_to_list(rows):
    return [dict(row) for row in rows]


def create_token(user):
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def get_token_user():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        db = get_db()

        user = db.execute(
            """
            SELECT id, name, email, role, active
            FROM users
            WHERE id = ?
            """,
            (payload["user_id"],)
        ).fetchone()

        if not user:
            return None

        if "active" in user.keys() and not user["active"]:
            return None

        return row_to_dict(user)

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        user = get_token_user()

        if not user:
            return jsonify({
                "message": "Authentication required"
            }), 401

        request.current_user = user

        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        user = get_token_user()

        if not user:
            return jsonify({
                "message": "Authentication required"
            }), 401

        if user["role"] != "admin":
            return jsonify({
                "message": "Admin access required"
            }), 403

        request.current_user = user

        return func(*args, **kwargs)

    return wrapper


def get_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def owner_filter(user, table_alias=""):
    """
    Returns SQL condition for admin/user data separation.

    Admin:
        Can see all records.

    User:
        Can only see records owned by that user.
    """

    if user["role"] == "admin":
        return "", ()

    prefix = f"{table_alias}." if table_alias else ""

    return f" AND {prefix}owner_id = ?", (user["id"],)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "SalesPro Sales Forecasting System API",
        "status": "running"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    })


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE LOWER(email) = LOWER(?)
        """,
        (email,)
    ).fetchone()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if "active" in user.keys() and not user["active"]:
        return jsonify({
            "message": "Your account is inactive"
        }), 403

    stored_password = user["password"]

    valid_password = False

    try:
        valid_password = check_password_hash(
            stored_password,
            password
        )
    except Exception:
        valid_password = stored_password == password

    if not valid_password:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    token = create_token(user)

    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "active": user["active"] if "active" in user.keys() else 1
    }

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user_data
    })


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "message": "Password must contain at least 6 characters"
        }), 400

    db = get_db()

    existing = db.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = LOWER(?)
        """,
        (email,)
    ).fetchone()

    if existing:
        return jsonify({
            "message": "Email already registered"
        }), 409

    password_hash = generate_password_hash(password)

    cursor = db.execute(
        """
        INSERT INTO users
        (name, email, password, role, active)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            password_hash,
            "user",
            1
        )
    )

    db.commit()

    return jsonify({
        "message": "Registration successful",
        "user_id": cursor.lastrowid
    }), 201


# ---------------------------------------------------------
# RESET PASSWORD
# ---------------------------------------------------------

@app.route("/api/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    account_role = data.get("role", "user").strip().lower()
    new_password = data.get("new_password", "")

    if account_role not in ("admin", "user"):
        return jsonify({"message": "Please select Admin or User account type"}), 400

    if not email or not new_password:
        return jsonify({
            "message": "Email and new password are required"
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "message": "Password must contain at least 6 characters"
        }), 400

    db = get_db()

    user = db.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = LOWER(?) AND LOWER(role) = LOWER(?)
        """,
        (email, account_role)
    ).fetchone()

    if not user:
        return jsonify({
            "message": "No account found with that email and selected account type"
        }), 404

    password_hash = generate_password_hash(new_password)

    db.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ?
        """,
        (
            password_hash,
            user["id"]
        )
    )

    db.commit()

    return jsonify({
        "message": "Password reset successful"
    })


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
@login_required
def dashboard():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user)

    products = db.execute(
        f"""
        SELECT COUNT(*) AS count
        FROM products
        WHERE 1=1 {condition}
        """,
        params
    ).fetchone()["count"]

    customers = db.execute(
        f"""
        SELECT COUNT(*) AS count
        FROM customers
        WHERE 1=1 {condition}
        """,
        params
    ).fetchone()["count"]

    sales_count = db.execute(
        f"""
        SELECT COUNT(*) AS count
        FROM sales
        WHERE 1=1 {condition}
        """,
        params
    ).fetchone()["count"]

    sales_total = db.execute(
        f"""
        SELECT COALESCE(SUM(total_amount), 0) AS total
        FROM sales
        WHERE 1=1 {condition}
        """,
        params
    ).fetchone()["total"]

    users_count = 0

    if user["role"] == "admin":
        users_count = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            """
        ).fetchone()["count"]

    recent_sales = db.execute(
        f"""
        SELECT
            s.id,
            s.invoice_no,
            s.product_name,
            s.customer_name,
            s.quantity,
            s.price,
            s.discount,
            s.tax,
            s.total_amount,
            s.sale_date,
            s.owner_id,
            u.name AS owner_name
        FROM sales s
        LEFT JOIN users u ON s.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY s.id DESC
        LIMIT 10
        """,
        params
    ).fetchall()

    return jsonify({
        "role": user["role"],
        "total_users": users_count,
        "total_products": products,
        "total_customers": customers,
        "total_sales": sales_total,
        "total_transactions": sales_count,
        "recent_sales": rows_to_list(recent_sales)
    })


# ---------------------------------------------------------
# USER MANAGEMENT - ADMIN
# ---------------------------------------------------------

@app.route("/api/admin/users", methods=["GET"])
@admin_required
def get_users():

    db = get_db()

    users = db.execute(
        """
        SELECT
            id,
            name,
            email,
            role,
            active
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    return jsonify({
        "users": rows_to_list(users)
    })


@app.route("/api/admin/users", methods=["POST"])
@admin_required
def create_user():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "user")

    if role not in ["admin", "user"]:
        role = "user"

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    db = get_db()

    existing = db.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = LOWER(?)
        """,
        (email,)
    ).fetchone()

    if existing:
        return jsonify({
            "message": "Email already exists"
        }), 409

    password_hash = generate_password_hash(password)

    cursor = db.execute(
        """
        INSERT INTO users
        (name, email, password, role, active)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            password_hash,
            role,
            1
        )
    )

    db.commit()

    return jsonify({
        "message": "User created successfully",
        "id": cursor.lastrowid
    }), 201


@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")
    role = data.get("role")

    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if role not in ["admin", "user"]:
        role = user["role"]

    db.execute(
        """
        UPDATE users
        SET name = ?,
            email = ?,
            role = ?
        WHERE id = ?
        """,
        (
            name if name else user["name"],
            email.lower() if email else user["email"],
            role,
            user_id
        )
    )

    db.commit()

    return jsonify({
        "message": "User updated successfully"
    })


@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):

    current_user = request.current_user

    if user_id == current_user["id"]:
        return jsonify({
            "message": "You cannot delete your own account"
        }), 400

    db = get_db()

    user = db.execute(
        """
        SELECT id
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    db.execute(
        """
        DELETE FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    db.commit()

    return jsonify({
        "message": "User deleted successfully"
    })


@app.route("/api/admin/users/<int:user_id>/toggle", methods=["PUT"])
@admin_required
def toggle_user(user_id):

    current_user = request.current_user

    if user_id == current_user["id"]:
        return jsonify({
            "message": "You cannot deactivate your own account"
        }), 400

    db = get_db()

    user = db.execute(
        """
        SELECT active
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    new_status = 0 if user["active"] else 1

    db.execute(
        """
        UPDATE users
        SET active = ?
        WHERE id = ?
        """,
        (
            new_status,
            user_id
        )
    )

    db.commit()

    return jsonify({
        "message": "User status updated",
        "active": new_status
    })


# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------

@app.route("/api/products", methods=["GET"])
@login_required
def get_products():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "p")

    products = db.execute(
        f"""
        SELECT
            p.*,
            u.name AS owner_name
        FROM products p
        LEFT JOIN users u ON p.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY p.id DESC
        """,
        params
    ).fetchall()

    return jsonify({
        "products": rows_to_list(products)
    })


@app.route("/api/products", methods=["POST"])
@login_required
def create_product():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    product_name = data.get("product_name", "").strip()
    category = data.get("category", "").strip()
    price = get_float(data.get("price"))
    stock_quantity = get_int(data.get("stock_quantity"))

    if not product_name:
        return jsonify({
            "message": "Product name is required"
        }), 400

    if price < 0 or stock_quantity < 0:
        return jsonify({
            "message": "Price and stock cannot be negative"
        }), 400

    owner_id = user["id"]

    if user["role"] == "admin" and data.get("owner_id"):
        owner_id = get_int(data.get("owner_id"), user["id"])

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO products
        (owner_id, product_name, category, price, stock_quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            product_name,
            category,
            price,
            stock_quantity
        )
    )

    db.commit()

    return jsonify({
        "message": "Product added successfully",
        "id": cursor.lastrowid
    }), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
@login_required
def update_product(product_id):

    user = request.current_user
    data = request.get_json(silent=True) or {}

    db = get_db()

    product = db.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if not product:
        return jsonify({
            "message": "Product not found"
        }), 404

    if user["role"] != "admin" and product["owner_id"] != user["id"]:
        return jsonify({
            "message": "You cannot update this product"
        }), 403

    product_name = data.get(
        "product_name",
        product["product_name"]
    )

    category = data.get(
        "category",
        product["category"]
    )

    price = get_float(
        data.get("price"),
        product["price"]
    )

    stock_quantity = get_int(
        data.get("stock_quantity"),
        product["stock_quantity"]
    )

    db.execute(
        """
        UPDATE products
        SET product_name = ?,
            category = ?,
            price = ?,
            stock_quantity = ?
        WHERE id = ?
        """,
        (
            product_name,
            category,
            price,
            stock_quantity,
            product_id
        )
    )

    db.commit()

    return jsonify({
        "message": "Product updated successfully"
    })


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id):

    user = request.current_user
    db = get_db()

    product = db.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if not product:
        return jsonify({
            "message": "Product not found"
        }), 404

    if user["role"] != "admin" and product["owner_id"] != user["id"]:
        return jsonify({
            "message": "You cannot delete this product"
        }), 403

    db.execute(
        """
        DELETE FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    db.commit()

    return jsonify({
        "message": "Product deleted successfully"
    })


# ---------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------

@app.route("/api/customers", methods=["GET"])
@login_required
def get_customers():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "c")

    customers = db.execute(
        f"""
        SELECT
            c.*,
            u.name AS owner_name
        FROM customers c
        LEFT JOIN users u ON c.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY c.id DESC
        """,
        params
    ).fetchall()

    return jsonify({
        "customers": rows_to_list(customers)
    })


@app.route("/api/customers", methods=["POST"])
@login_required
def create_customer():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    customer_code = data.get("customer_code", "").strip()
    name = data.get("customer_name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()

    if not name:
        return jsonify({
            "message": "Customer name is required"
        }), 400

    owner_id = user["id"]

    if user["role"] == "admin" and data.get("owner_id"):
        owner_id = get_int(data.get("owner_id"), user["id"])

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO customers
        (owner_id, customer_code, customer_name, phone, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            customer_code or None,
            name,
            phone,
            email,
            address
        )
    )

    db.commit()

    return jsonify({
        "message": "Customer added successfully",
        "id": cursor.lastrowid
    }), 201


@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
@login_required
def update_customer(customer_id):

    user = request.current_user
    data = request.get_json(silent=True) or {}

    db = get_db()

    customer = db.execute(
        """
        SELECT *
        FROM customers
        WHERE id = ?
        """,
        (customer_id,)
    ).fetchone()

    if not customer:
        return jsonify({
            "message": "Customer not found"
        }), 404

    if user["role"] != "admin" and customer["owner_id"] != user["id"]:
        return jsonify({
            "message": "You cannot update this customer"
        }), 403

    db.execute(
        """
        UPDATE customers
        SET customer_code = ?,
            customer_name = ?,
            phone = ?,
            email = ?,
            address = ?
        WHERE id = ?
        """,
        (
            data.get("customer_code", customer["customer_code"] if "customer_code" in customer.keys() else None),
            data.get(
                "customer_name",
                customer["customer_name"]
            ),
            data.get(
                "phone",
                customer["phone"]
            ),
            data.get(
                "email",
                customer["email"]
            ),
            data.get(
                "address",
                customer["address"]
            ),
            customer_id
        )
    )

    db.commit()

    return jsonify({
        "message": "Customer updated successfully"
    })


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
@login_required
def delete_customer(customer_id):

    user = request.current_user
    db = get_db()

    customer = db.execute(
        """
        SELECT *
        FROM customers
        WHERE id = ?
        """,
        (customer_id,)
    ).fetchone()

    if not customer:
        return jsonify({
            "message": "Customer not found"
        }), 404

    if user["role"] != "admin" and customer["owner_id"] != user["id"]:
        return jsonify({
            "message": "You cannot delete this customer"
        }), 403

    db.execute(
        """
        DELETE FROM customers
        WHERE id = ?
        """,
        (customer_id,)
    )

    db.commit()

    return jsonify({
        "message": "Customer deleted successfully"
    })


# ---------------------------------------------------------
# SALES
# ---------------------------------------------------------

@app.route("/api/sales", methods=["GET"])
@login_required
def get_sales():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "s")

    sales = db.execute(
        f"""
        SELECT
            s.*,
            u.name AS owner_name
        FROM sales s
        LEFT JOIN users u ON s.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY s.id DESC
        """,
        params
    ).fetchall()

    return jsonify({
        "sales": rows_to_list(sales)
    })


@app.route("/api/sales", methods=["POST"])
@login_required
def create_sale():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    product_name = data.get("product_name", "").strip()
    customer_name = data.get("customer_name", "").strip()

    quantity = get_int(data.get("quantity"), 1)
    price = get_float(data.get("price"))
    discount = get_float(data.get("discount"))
    tax = get_float(data.get("tax"))

    sale_date = data.get(
        "sale_date",
        datetime.now().strftime("%Y-%m-%d")
    )

    invoice_no = data.get(
        "invoice_no",
        f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    if not product_name:
        return jsonify({
            "message": "Product name is required"
        }), 400

    if quantity <= 0:
        return jsonify({
            "message": "Quantity must be greater than zero"
        }), 400

    subtotal = quantity * price
    total_amount = subtotal - discount + tax

    if total_amount < 0:
        total_amount = 0

    owner_id = user["id"]

    if user["role"] == "admin" and data.get("owner_id"):
        owner_id = get_int(
            data.get("owner_id"),
            user["id"]
        )

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO sales
        (
            owner_id,
            invoice_no,
            product_name,
            customer_name,
            quantity,
            price,
            discount,
            tax,
            sale_date,
            total_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            invoice_no,
            product_name,
            customer_name,
            quantity,
            price,
            discount,
            tax,
            sale_date,
            total_amount
        )
    )

    # Reduce stock if matching product belongs to the owner.
    product = db.execute(
        """
        SELECT id, stock_quantity
        FROM products
        WHERE product_name = ?
          AND owner_id = ?
        LIMIT 1
        """,
        (
            product_name,
            owner_id
        )
    ).fetchone()

    if product:
        new_stock = max(
            0,
            product["stock_quantity"] - quantity
        )

        db.execute(
            """
            UPDATE products
            SET stock_quantity = ?
            WHERE id = ?
            """,
            (
                new_stock,
                product["id"]
            )
        )

    db.commit()

    return jsonify({
        "message": "Sale added successfully",
        "id": cursor.lastrowid,
        "total_amount": total_amount
    }), 201


@app.route("/api/sales/<int:sale_id>", methods=["PUT"])
@login_required
def update_sale(sale_id):

    user = request.current_user
    data = request.get_json(silent=True) or {}

    db = get_db()

    sale = db.execute(
        """
        SELECT *
        FROM sales
        WHERE id = ?
        """,
        (sale_id,)
    ).fetchone()

    if not sale:
        return jsonify({
            "message": "Sale not found"
        }), 404

    if user["role"] != "admin" and sale["owner_id"] != user["id"]:
        return jsonify({
            "message": "You cannot update this sale"
        }), 403

    product_name = data.get(
        "product_name",
        sale["product_name"]
    )

    customer_name = data.get(
        "customer_name",
        sale["customer_name"]
    )

    quantity = get_int(
        data.get("quantity"),
        sale["quantity"]
    )

    price = get_float(
        data.get("price"),
        sale["price"]
    )

    discount = get_float(
        data.get("discount"),
        sale["discount"]
    )

    tax = get_float(
        data.get("tax"),
        sale["tax"]
    )

    sale_date = data.get(
        "sale_date",
        sale["sale_date"]
    )

    invoice_no = data.get(
        "invoice_no",
        sale["invoice_no"]
    )

    total_amount = (
        quantity * price
    ) - discount + tax

    if total_amount < 0:
        total_amount = 0

    db.execute(
        """
        UPDATE sales
        SET invoice_no = ?,
            product_name = ?,
            customer_name = ?,
            quantity = ?,
            price = ?,
            discount = ?,
            tax = ?,
            sale_date = ?,
            total_amount = ?
        WHERE id = ?
        """,
        (
            invoice_no,
            product_name,
            customer_name,
            quantity,
            price,
            discount,
            tax,
            sale_date,
            total_amount,
            sale_id
        )
    )

    db.commit()

    return jsonify({
        "message": "Sale updated successfully"
    })


@app.route("/api/sales/<int:sale_id>", methods=["DELETE"])
@login_required
def delete_sale(sale_id):

    user = request.current_user
    db = get_db()

    sale = db.execute(
        """
        SELECT *
        FROM sales
        WHERE id = ?
        """,
        (sale_id,)
    ).fetchone()

    if not sale:
        return jsonify({
            "message": "Sale not found"
        }), 404

    if user["role"] != "admin" and sale["owner_id"] != user["id"]:
        return jsonify({
            "message": "You cannot delete this sale"
        }), 403

    db.execute(
        """
        DELETE FROM sales
        WHERE id = ?
        """,
        (sale_id,)
    )

    db.commit()

    return jsonify({
        "message": "Sale deleted successfully"
    })


# ---------------------------------------------------------
# FORECASTING
# ---------------------------------------------------------

@app.route("/api/forecast", methods=["GET", "POST"])
@login_required
def forecast():

    user = request.current_user
    db = get_db()

    data = (
        request.get_json(silent=True) or {}
        if request.method == "POST"
        else request.args
    )

    product_name = data.get("product_name")

    condition, params = owner_filter(user, "s")

    if product_name:
        condition += " AND LOWER(s.product_name) = LOWER(?)"
        params = (*params, product_name)

    sales_rows = db.execute(
        f"""
        SELECT
            sale_date,
            SUM(total_amount) AS total
        FROM sales s
        WHERE 1=1 {condition}
        GROUP BY sale_date
        ORDER BY sale_date
        """,
        params
    ).fetchall()

    actual_values = [
        float(row["total"] or 0)
        for row in sales_rows
    ]

    dates = [
        row["sale_date"]
        for row in sales_rows
    ]

    if not actual_values:
        return jsonify({
            "product_name": product_name,
            "actual": [],
            "predicted": [],
            "accuracy": 0,
            "message": "No sales data available for forecasting"
        })

    # Simple moving-average forecasting suitable for
    # a college project demonstration.
    window = min(3, len(actual_values))

    recent_values = actual_values[-window:]

    predicted_value = (
        sum(recent_values) / len(recent_values)
    )

    predicted = [
        round(predicted_value, 2)
        for _ in range(5)
    ]

    # Basic historical accuracy estimation.
    if len(actual_values) >= 2:

        errors = []

        for index in range(1, len(actual_values)):

            previous_start = max(
                0,
                index - window
            )

            previous = actual_values[
                previous_start:index
            ]

            if not previous:
                continue

            prediction = sum(previous) / len(previous)
            actual = actual_values[index]

            if actual != 0:
                error = abs(
                    actual - prediction
                ) / abs(actual)

                errors.append(error)

        if errors:
            accuracy = max(
                0,
                100 - (
                    sum(errors) / len(errors) * 100
                )
            )
        else:
            accuracy = 100
    else:
        accuracy = 0

    return jsonify({
        "product_name": product_name,
        "dates": dates,
        "actual": actual_values,
        "predicted": predicted,
        "forecast_next_5": predicted,
        "accuracy": round(accuracy, 2)
    })


# ---------------------------------------------------------
# REPORTS
# ---------------------------------------------------------

@app.route("/api/reports", methods=["GET"])
@login_required
def reports():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "s")

    daily = db.execute(
        f"""
        SELECT
            sale_date,
            COUNT(*) AS transactions,
            COALESCE(SUM(total_amount), 0) AS total
        FROM sales s
        WHERE 1=1 {condition}
        GROUP BY sale_date
        ORDER BY sale_date DESC
        """,
        params
    ).fetchall()

    monthly = db.execute(
        f"""
        SELECT
            SUBSTR(sale_date, 1, 7) AS month,
            COUNT(*) AS transactions,
            COALESCE(SUM(total_amount), 0) AS total
        FROM sales s
        WHERE 1=1 {condition}
        GROUP BY SUBSTR(sale_date, 1, 7)
        ORDER BY month DESC
        """,
        params
    ).fetchall()

    yearly = db.execute(
        f"""
        SELECT
            SUBSTR(sale_date, 1, 4) AS year,
            COUNT(*) AS transactions,
            COALESCE(SUM(total_amount), 0) AS total
        FROM sales s
        WHERE 1=1 {condition}
        GROUP BY SUBSTR(sale_date, 1, 4)
        ORDER BY year DESC
        """,
        params
    ).fetchall()

    products = db.execute(
        f"""
        SELECT
            product_name,
            SUM(quantity) AS quantity,
            COALESCE(SUM(total_amount), 0) AS revenue
        FROM sales s
        WHERE 1=1 {condition}
        GROUP BY product_name
        ORDER BY revenue DESC
        """,
        params
    ).fetchall()

    customers = db.execute(
        f"""
        SELECT
            customer_name,
            COUNT(*) AS transactions,
            COALESCE(SUM(total_amount), 0) AS total
        FROM sales s
        WHERE 1=1 {condition}
        GROUP BY customer_name
        ORDER BY total DESC
        """,
        params
    ).fetchall()

    return jsonify({
        "daily": rows_to_list(daily),
        "weekly": [],
        "monthly": rows_to_list(monthly),
        "yearly": rows_to_list(yearly),
        "products": rows_to_list(products),
        "customers": rows_to_list(customers)
    })


# ---------------------------------------------------------
# CSV REPORT
# ---------------------------------------------------------

@app.route("/api/reports/sales.csv", methods=["GET"])
@login_required
def sales_csv():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "s")

    sales = db.execute(
        f"""
        SELECT
            s.id,
            s.invoice_no,
            s.product_name,
            s.customer_name,
            s.quantity,
            s.price,
            s.discount,
            s.tax,
            s.total_amount,
            s.sale_date,
            u.name AS owner_name
        FROM sales s
        LEFT JOIN users u
            ON s.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY s.id DESC
        """,
        params
    ).fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Invoice No",
        "Product",
        "Customer",
        "Quantity",
        "Price",
        "Discount",
        "Tax",
        "Total Amount",
        "Sale Date",
        "Owner"
    ])

    for sale in sales:
        writer.writerow([
            sale["id"],
            sale["invoice_no"],
            sale["product_name"],
            sale["customer_name"],
            sale["quantity"],
            sale["price"],
            sale["discount"],
            sale["tax"],
            sale["total_amount"],
            sale["sale_date"],
            sale["owner_name"]
        ])

    response = make_response(output.getvalue())

    response.headers["Content-Type"] = "text/csv"
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=sales_report.csv"

    return response


# ---------------------------------------------------------
# CATEGORY MANAGEMENT
# ---------------------------------------------------------

@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():

    db = get_db()

    categories = db.execute(
        """
        SELECT *
        FROM categories
        ORDER BY id DESC
        """
    ).fetchall()

    return jsonify({
        "categories": rows_to_list(categories)
    })


@app.route("/api/categories", methods=["POST"])
@login_required
def create_category():

    data = request.get_json(silent=True) or {}

    name = data.get(
        "name",
        data.get("category_name", "")
    ).strip()

    if not name:
        return jsonify({
            "message": "Category name is required"
        }), 400

    db = get_db()

    existing = db.execute(
        """
        SELECT id
        FROM categories
        WHERE LOWER(name) = LOWER(?)
        """,
        (name,)
    ).fetchone()

    if existing:
        return jsonify({
            "message": "Category already exists"
        }), 409

    cursor = db.execute(
        """
        INSERT INTO categories
        (name)
        VALUES (?)
        """,
        (name,)
    )

    db.commit()

    return jsonify({
        "message": "Category added successfully",
        "id": cursor.lastrowid
    }), 201


# ---------------------------------------------------------
# SUPPLIER MANAGEMENT
# ---------------------------------------------------------

@app.route("/api/suppliers", methods=["GET"])
@login_required
def get_suppliers():

    db = get_db()

    suppliers = db.execute(
        """
        SELECT *
        FROM suppliers
        ORDER BY id DESC
        """
    ).fetchall()

    return jsonify({
        "suppliers": rows_to_list(suppliers)
    })


@app.route("/api/suppliers", methods=["POST"])
@login_required
def create_supplier():

    data = request.get_json(silent=True) or {}

    name = data.get(
        "name",
        data.get("supplier_name", "")
    ).strip()

    contact = data.get(
        "contact",
        data.get("contact_number", "")
    ).strip()

    email = data.get(
        "email",
        ""
    ).strip()

    address = data.get(
        "address",
        ""
    ).strip()

    if not name:
        return jsonify({
            "message": "Supplier name is required"
        }), 400

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO suppliers
        (name, contact, email, address)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            contact,
            email,
            address
        )
    )

    db.commit()

    return jsonify({
        "message": "Supplier added successfully",
        "id": cursor.lastrowid
    }), 201


# ---------------------------------------------------------
# PURCHASE / STOCK IN
# ---------------------------------------------------------

@app.route("/api/purchases", methods=["GET"])
@login_required
def get_purchases():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "p")

    purchases = db.execute(
        f"""
        SELECT
            p.*,
            u.name AS owner_name
        FROM purchases p
        LEFT JOIN users u
            ON p.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY p.id DESC
        """,
        params
    ).fetchall()

    return jsonify({
        "purchases": rows_to_list(purchases)
    })


@app.route("/api/purchases", methods=["POST"])
@login_required
def create_purchase():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    supplier = data.get(
        "supplier_name",
        data.get("supplier", "")
    ).strip()

    product_name = data.get(
        "product_name",
        ""
    ).strip()

    quantity = get_int(
        data.get("quantity")
    )

    purchase_price = get_float(
        data.get("purchase_price")
    )

    purchase_date = data.get(
        "purchase_date",
        datetime.now().strftime("%Y-%m-%d")
    )

    if not product_name or quantity <= 0:
        return jsonify({
            "message": "Product and valid quantity are required"
        }), 400

    owner_id = user["id"]

    if user["role"] == "admin" and data.get("owner_id"):
        owner_id = get_int(
            data.get("owner_id"),
            user["id"]
        )

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO purchases
        (
            owner_id,
            supplier_name,
            product_name,
            quantity,
            purchase_price,
            purchase_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            supplier,
            product_name,
            quantity,
            purchase_price,
            purchase_date
        )
    )

    product = db.execute(
        """
        SELECT id, stock_quantity
        FROM products
        WHERE LOWER(product_name) = LOWER(?)
          AND owner_id = ?
        LIMIT 1
        """,
        (
            product_name,
            owner_id
        )
    ).fetchone()

    if product:

        new_stock = (
            product["stock_quantity"] + quantity
        )

        db.execute(
            """
            UPDATE products
            SET stock_quantity = ?
            WHERE id = ?
            """,
            (
                new_stock,
                product["id"]
            )
        )

    db.commit()

    return jsonify({
        "message": "Purchase added and stock updated",
        "id": cursor.lastrowid
    }), 201


# ---------------------------------------------------------
# SALES RETURNS
# ---------------------------------------------------------

@app.route("/api/returns", methods=["GET"])
@login_required
def get_returns():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "r")

    returns = db.execute(
        f"""
        SELECT
            r.*,
            u.name AS owner_name
        FROM sales_returns r
        LEFT JOIN users u
            ON r.owner_id = u.id
        WHERE 1=1 {condition}
        ORDER BY r.id DESC
        """,
        params
    ).fetchall()

    return jsonify({
        "returns": rows_to_list(returns)
    })


@app.route("/api/returns", methods=["POST"])
@login_required
def create_return():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    invoice_no = data.get(
        "invoice_no",
        ""
    ).strip()

    product_name = data.get(
        "product_name",
        ""
    ).strip()

    quantity = get_int(
        data.get("return_quantity"),
        get_int(data.get("quantity"))
    )

    reason = data.get(
        "reason",
        ""
    ).strip()

    refund_amount = get_float(
        data.get("refund_amount")
    )

    if not invoice_no or not product_name or quantity <= 0:
        return jsonify({
            "message": "Invoice, product and valid quantity are required"
        }), 400

    owner_id = user["id"]

    if user["role"] == "admin" and data.get("owner_id"):
        owner_id = get_int(
            data.get("owner_id"),
            user["id"]
        )

    db = get_db()

    sale = db.execute(
        """
        SELECT *
        FROM sales
        WHERE invoice_no = ?
          AND owner_id = ?
        LIMIT 1
        """,
        (
            invoice_no,
            owner_id
        )
    ).fetchone()

    if not sale:
        return jsonify({
            "message": "Sale invoice not found"
        }), 404

    if quantity > sale["quantity"]:
        return jsonify({
            "message": "Return quantity cannot exceed sold quantity"
        }), 400

    if refund_amount <= 0:
        refund_amount = (
            sale["price"] * quantity
        )

    cursor = db.execute(
        """
        INSERT INTO sales_returns
        (
            owner_id,
            invoice_no,
            product_name,
            return_quantity,
            reason,
            refund_amount,
            return_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            invoice_no,
            product_name,
            quantity,
            reason,
            refund_amount,
            datetime.now().strftime("%Y-%m-%d")
        )
    )

    product = db.execute(
        """
        SELECT id, stock_quantity
        FROM products
        WHERE LOWER(product_name) = LOWER(?)
          AND owner_id = ?
        LIMIT 1
        """,
        (
            product_name,
            owner_id
        )
    ).fetchone()

    if product:

        new_stock = (
            product["stock_quantity"] + quantity
        )

        db.execute(
            """
            UPDATE products
            SET stock_quantity = ?
            WHERE id = ?
            """,
            (
                new_stock,
                product["id"]
            )
        )

    db.commit()

    return jsonify({
        "message": "Sales return recorded successfully",
        "id": cursor.lastrowid
    }), 201


# ---------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------

@app.route("/api/notifications", methods=["GET"])
@login_required
def notifications():

    user = request.current_user
    db = get_db()

    condition, params = owner_filter(user, "p")

    low_stock = db.execute(
        f"""
        SELECT
            p.id,
            p.product_name,
            p.stock_quantity,
            p.owner_id,
            u.name AS owner_name
        FROM products p
        LEFT JOIN users u
            ON p.owner_id = u.id
        WHERE p.stock_quantity <= 5
        {condition}
        ORDER BY p.stock_quantity ASC
        """,
        params
    ).fetchall()

    notifications_list = []

    for product in low_stock:

        notifications_list.append({
            "type": "low_stock",
            "title": "Low Stock Alert",
            "message": (
                f"{product['product_name']} has only "
                f"{product['stock_quantity']} items left."
            ),
            "product_id": product["id"],
            "owner_name": product["owner_name"]
        })

    return jsonify({
        "notifications": notifications_list,
        "count": len(notifications_list)
    })


# ---------------------------------------------------------
# PROFILE
# ---------------------------------------------------------

@app.route("/api/profile", methods=["GET"])
@login_required
def get_profile():

    user = request.current_user

    return jsonify({
        "user": user
    })


@app.route("/api/profile", methods=["PUT"])
@login_required
def update_profile():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    name = data.get(
        "name",
        user["name"]
    ).strip()

    email = data.get(
        "email",
        user["email"]
    ).strip().lower()

    if not name or not email:
        return jsonify({
            "message": "Name and email are required"
        }), 400

    db = get_db()

    existing = db.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = LOWER(?)
          AND id != ?
        """,
        (
            email,
            user["id"]
        )
    ).fetchone()

    if existing:
        return jsonify({
            "message": "Email already in use"
        }), 409

    db.execute(
        """
        UPDATE users
        SET name = ?,
            email = ?
        WHERE id = ?
        """,
        (
            name,
            email,
            user["id"]
        )
    )

    db.commit()

    updated_user = db.execute(
        """
        SELECT id, name, email, role, active
        FROM users
        WHERE id = ?
        """,
        (user["id"],)
    ).fetchone()

    return jsonify({
        "message": "Profile updated successfully",
        "user": row_to_dict(updated_user)
    })


@app.route("/api/profile/password", methods=["PUT"])
@login_required
def change_password():

    user = request.current_user
    data = request.get_json(silent=True) or {}

    current_password = data.get(
        "current_password",
        ""
    )

    new_password = data.get(
        "new_password",
        ""
    )

    if not current_password or not new_password:
        return jsonify({
            "message": "Current and new password are required"
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "message": "New password must contain at least 6 characters"
        }), 400

    db = get_db()

    database_user = db.execute(
        """
        SELECT password
        FROM users
        WHERE id = ?
        """,
        (user["id"],)
    ).fetchone()

    if not database_user:
        return jsonify({
            "message": "User not found"
        }), 404

    if not check_password_hash(
        database_user["password"],
        current_password
    ):
        return jsonify({
            "message": "Current password is incorrect"
        }), 401

    password_hash = generate_password_hash(
        new_password
    )

    db.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ?
        """,
        (
            password_hash,
            user["id"]
        )
    )

    db.commit()

    return jsonify({
        "message": "Password changed successfully"
    })


# ---------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "message": "API endpoint not found"
    }), 404


@app.errorhandler(500)
def server_error(error):

    return jsonify({
        "message": "Internal server error",
        "error": str(error)
    }), 500


# ---------------------------------------------------------
# APPLICATION START
# ---------------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )