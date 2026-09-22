# The code isn't complete for security reasons
# login | register | authentication | authorization | session management | invoice management | coupon management
from flask import Flask, render_template, flash, request, redirect, url_for, abort, session, logging, jsonify
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# name app
app = Flask(__name__)

# data by batabase
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
app.config["MYSQL_CURSORCLASS"] = os.getenv("MYSQL_CURSORCLASS")  # لتحويل الاستعلامات  dict

mysql = MySQL(app)

# session timeout
app.permanent_session_lifetime = timedelta(minutes=30)


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "css", "icon")
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)


def allowed_image_filename(filename):
    return (bool(filename) and "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS)

def save_image_file(file_storage):
    if not file_storage or not allowed_image_filename(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    dest = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
    file_storage.save(dest)
    return filename


# home
@app.route("/")
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT* FROM products")
    data = cur.fetchall()
    return render_template("home.html", data=data)


@abdo.route('/details/<int:products_id>', methods=['GET'])
def products_details(products_id):
    cur = mysql.connection.cursor() 
    cur.execute("""SELECT p.*, d.attribute, d.value FROM products p LEFT JOIN product_details d ON p.id = d.product_id WHERE p.id = %s""", (products_id,))
    
    product = cur.fetchall()
    cur.close()

    if not product:
        return redirect(url_for('not_found'))

    product_dict = dict(product[0])
    product_dict['details'] = {}  

    for row in product:
        if row['attribute']:
            product_dict['details'][row['attribute']] = row['value']

    return render_template("details.html", product=product_dict, products_id=products_id)


# search
@app.route("/search", methods=["GET", "POST"])
def search():
    cur = mysql.connection.cursor()
    search_query = request.args.get("search-input", "").strip()
    if search_query:
        cur.execute(
            "SELECT * FROM products WHERE name LIKE %s",
            tuple("%" + search_query + "%" for _ in range(1)),
        )

        mobiles = cur.fetchall()
        if mobiles:
            return render_template("mobile.html", mobiles=mobiles)
        else:
            session["search_query"] = search_query
            flash(
                f"No mobiles found matching your search: {session['search_query']}",
                "danger",
            )

            return redirect(url_for("search"))

    # لو مفيش كلمة بحث
    cur.execute("SELECT * FROM products WHERE category='mobile' ")
    mobiles = cur.fetchall()
    return render_template("mobile.html", mobiles=mobiles)


def logged_in(role=None):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "logged_in" not in session:
                flash("⚠️ Unauthorized, Please login first.", "danger")
                return redirect(url_for("login"))

            if role:
                user_role = session.get("role")
                allowed_roles = role if isinstance(role, list) else [role]
                if user_role not in allowed_roles:
                    flash("🚫 Access denied: insufficient permissions.", "warning")
                    return redirect(url_for("dashboard"))
            return f(*args, **kwargs)

        return wrap

    return decorator


def get_invoice_id():
    invoice_id = session.get('invoice_id')
    if not invoice_id:  
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO invoices (created_at, user_id) VALUES (NOW(), %s)", (session.get('user_id'),))
        mysql.connection.commit()
        invoice_id = cur.lastrowid 
        session['invoice_id'] = invoice_id
        cur.close() 
    return invoice_id

def get_invoice_item(invoice_id, product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM invoice_items WHERE invoice_id=%s AND product_id=%s",(invoice_id, product_id))
    item = cur.fetchone()
    cur.close()
    return item


def update_quantity(invoice_id, product_id, quantity):
    cur = mysql.connection.cursor()
    if quantity > 0:
        cur.execute("UPDATE invoice_items SET quantity=%s WHERE invoice_id=%s AND product_id=%s",
                    (quantity, invoice_id, product_id))
    else:
        cur.execute("DELETE FROM invoice_items WHERE invoice_id=%s AND product_id=%s",
                    (invoice_id, product_id))
    mysql.connection.commit()
    cur.close()

# ===============
# add product to invoice |
# ===============
@abdo.route('/add_to_invoice/<int:product_id>', methods=['GET', 'POST'])
def add_to_invoice(product_id):
    invoice_id = get_invoice_id()  # create invoice

    # تأكد أن المنتج موجود
    cur = mysql.connection.cursor()
    # تأكد من تحديد الأعمدة أو استخدام '*' في SELECT
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    if not product:
        flash("This product does not exist.", "danger")
        return redirect(url_for('show_invoice'))

    # تحقق من وجود المنتج بالفعل في الفاتورة
    item = get_invoice_item(invoice_id, product_id)

    if item:
        if item['quantity'] >= 2:
            flash("Maximum quantity reached (2 items per product).", "warning")
        else:
            update_quantity(invoice_id, product_id, item['quantity'] + 1)
    else:
        cur.execute("""
            INSERT INTO invoice_items (invoice_id, product_id, quantity) 
            VALUES (%s, %s, 1)
        """, (invoice_id, product_id))
        mysql.connection.commit()
    
    cur.close()
    return redirect(url_for('show_invoice'))

#====================================================================
@abdo.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    invoice_id = session.get('invoice_id')
    if not invoice_id:
        flash("No active invoice!", "danger")
        return redirect(url_for('show_invoice'))

    code = request.form.get('coupon-code').strip()
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM discount WHERE code=%s", (code,))
           ## OR ##
    # coupon = cur.fetchone()
    # cur.execute("""SELECT * FROM discount WHERE code=%s
    #          AND expiry_date >= CURDATE()
    #          AND used_count < usage_limit """, (coupon_code,))
    coupon = cur.fetchone()
    if not coupon:
        flash(f"❌ Invalid coupon code{code}.", "danger")
        return redirect(url_for('show_invoice'))
    # تحقق من تاريخ الصلاحية
    if coupon['expiry_date'] and datetime.now().date() > coupon['expiry_date']:
        flash("❌ Coupon expired.", "danger")
        return redirect(url_for('show_invoice'))

    # تحقق من مرات الاستخدام
    elif coupon['used_count'] >= coupon['usage_limit']:
        flash("❌ Coupon usage limit reached.", "danger")
        return redirect(url_for('show_invoice'))

    session['code'] = coupon
    flash("✅ Coupon applied successfully!", "success")

    return redirect(url_for('show_invoice'))

# ==========================================================
# عرض الفاتورة                                            |
# ==========================================================
@abdo.route('/invoice')
def show_invoice():
    invoice_id = session.get('invoice_id')
    if not invoice_id:
        return render_template('invoice.html', invoice_items=None)
   
    else:
        cur = mysql.connection.cursor()
        cur.execute("""
                SELECT ii.product_id,p.name, p.price,p.image, ii.quantity, ii.datetimes AS datetime, 
                (p.price * ii.quantity) AS subtotal
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = %s""", 
                (invoice_id,))
        items = cur.fetchall()
        cur.close()

    try:
        total = sum(item['subtotal'] for item in items)
        total_items = sum(item['quantity'] for item in items)
    except (TypeError, KeyError, IndexError):
        total = sum(item[6] for item in items)
        total_items = sum(item[4] for item in items)

    discount = 0
    final_total = total
    # read coupon from session - support older key 'coupon' and newer 'code'
    coupon = session.get('code') or session.get('coupon')
    if coupon:
        # إذا نوع الخصم نسبة مئوية
        discount_value = coupon.get('discount_value', 0)
        try:
            discount_value = float(discount_value)
        except (TypeError, ValueError):
            discount_value = 0
        if coupon.get('discount_type') == 'percent':
            discount = total * (discount_value / 100)
        else:  # مبلغ ثابت
            discount = discount_value
        final_total = max(0, total - discount)
        
    return render_template('invoice.html', invoice_items=items, total=total, total_items=total_items, discount=discount, final_total=final_total, coupon=coupon)

# =============
# del item    |
# =============
@abdo.route('/remove_from_invoice/<int:product_id>', methods=['POST'])
def remove_from_invoice(product_id):
    invoice_id = session.get('invoice_id')
    if invoice_id:
        update_quantity(invoice_id, product_id, 0)
    return redirect(url_for('show_invoice'))

# ===============
# increase_quantity |
# ===============
@abdo.route('/increase_quantity/<int:product_id>', methods=['POST'])
def increase_quantity(product_id):
    invoice_id = session.get('invoice_id')
    item = get_invoice_item(invoice_id, product_id)

    if item:
        if item['quantity'] < 2:
            update_quantity(invoice_id, product_id, item['quantity'] + 1)
        else:
            flash("Maximum quantity reached (2 items per product).", "warning")

    return redirect(url_for('show_invoice'))

# =============== 
#  decrease quantity |
# ===============
@abdo.route('/decrease_quantity/<int:product_id>', methods=['POST'])
def decrease_quantity(product_id):
    invoice_id = session.get('invoice_id')
    item = get_invoice_item(invoice_id, product_id)

    if item:
        update_quantity(invoice_id, product_id, item['quantity'] - 1)

    return redirect(url_for('show_invoice'))

# =========================
# delete invoice
# =========================
@abdo.route('/clear_invoice', methods=['POST'])
def clear_invoice():
    invoice_id = session.get('invoice_id')
    if invoice_id:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM invoice_items WHERE invoice_id=%s", (invoice_id,))
        mysql.connection.commit()
        cur.close()
        session.pop('invoice_id',None)
    return redirect(url_for('show_invoice'))

@abdo.route('/logout')
def logout():
    if session.get('logged_in'):
        session.clear() 
        flash('You have been logged out', 'success')
    else:
        flash('You are not logged in Crezy', 'danger')
    return redirect(url_for('home'))

@abdo.route('/not_found')
def not_found():
    return render_template('not_found.html')


if __name__ == "__main__": 
    secret_key = os.getenv("SECRET_KEY")
    abdo.run(debug=True, port=8000)



# The code isn't complete for security reasons
