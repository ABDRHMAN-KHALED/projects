import hashlib
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

# --- 1. إعداد قاعدة البيانات ---
DB_NAME = "app_system.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # جدول بيانات المستخدمين (لإضافة البيانات الخاصة بكل مستخدم)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # جدول سجلات النشاطات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action_type TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # حساب تجريبي (المستخدم: admin / كلمة السر: admin123)
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            ("admin", hashed_pw, now),
        )

    conn.commit()
    conn.close()


def log_activity(username, action_type):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO activity_logs (username, action_type, timestamp) VALUES (?, ?, ?)",
            (username, action_type, now),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


# --- 2. التطبيق الرئيسي ---
class FullSystemApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("app")
        self.geometry("520x650")
        self.resizable(False, False)

        self.configure(bg="#f4f6f9")
        self.current_user = None

        init_db()

        self.main_container = tk.Frame(self, bg="#f4f6f9")
        self.main_container.pack(fill="both", expand=True)

        self.show_login_frame()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ==================== 1. تسجيل الدخول ====================
    def show_login_frame(self):
        self.clear_container()

        frame = tk.Frame(
            self.main_container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=25,
            pady=25,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=420, height=450)

        lbl_title = tk.Label(
            frame,
            text="تسجيل الدخول",
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
            fg="#333333",
        )
        lbl_title.pack(pady=(10, 20))

        lbl_user = tk.Label(
            frame,
            text="اسم المستخدم:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_user.pack(fill="x", pady=(5, 2))
        self.ent_username = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            justify="right",
        )
        self.ent_username.pack(fill="x", ipady=4, pady=(0, 15))

        lbl_pass = tk.Label(
            frame,
            text="كلمة المرور:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_pass.pack(fill="x", pady=(5, 2))
        self.ent_password = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            show="•",
            justify="right",
        )
        self.ent_password.pack(fill="x", ipady=4, pady=(0, 15))

        btn_login = tk.Button(
            frame,
            text="تسجيل الدخول",
            font=("Segoe UI", 11, "bold"),
            bg="#28a745",
            fg="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.login_process,
        )
        btn_login.pack(fill="x", ipady=6, pady=(10, 5))

        btn_register = tk.Button(
            frame,
            text="إنشاء حساب جديد",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#007bff",
            bd=0,
            cursor="hand2",
            command=self.show_register_frame,
        )
        btn_register.pack(pady=5)

    def login_process(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        if not username or not password:
            messagebox.showwarning("تنبيه", "يرجى إدخال الحقول المطلوبة!")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, hashed_pw),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            self.current_user = username
            log_activity(username, "تسجيل دخول")
            self.show_dashboard_frame()
        else:
            messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة!")

    # ==================== إنشاء حساب ====================
    def show_register_frame(self):
        self.clear_container()
        frame = tk.Frame(
            self.main_container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=25,
            pady=25,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=420, height=420)

        lbl_title = tk.Label(
            frame,
            text="حساب جديد",
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
            fg="#333333",
        )
        lbl_title.pack(pady=(10, 20))

        lbl_user = tk.Label(
            frame,
            text="اسم المستخدم:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_user.pack(fill="x", pady=(5, 2))
        self.reg_username = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            justify="right",
        )
        self.reg_username.pack(fill="x", ipady=4, pady=(0, 10))

        lbl_pass = tk.Label(
            frame,
            text="كلمة المرور:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_pass.pack(fill="x", pady=(5, 2))
        self.reg_password = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            show="•",
            justify="right",
        )
        self.reg_password.pack(fill="x", ipady=4, pady=(0, 15))

        btn_submit = tk.Button(
            frame,
            text="تسجيل الحساب",
            font=("Segoe UI", 11, "bold"),
            bg="#007bff",
            fg="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.register_process,
        )
        btn_submit.pack(fill="x", ipady=6, pady=(5, 5))

        btn_back = tk.Button(
            frame,
            text="رجوع",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6c757d",
            bd=0,
            cursor="hand2",
            command=self.show_login_frame,
        )
        btn_back.pack(pady=5)

    def register_process(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        if not username or not password:
            messagebox.showwarning("تنبيه", "املأ جميع الحقول!")
            return
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, hashed_pw, now),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("نجاح", "تم الحساب بنجاح!")
            self.show_login_frame()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "اسم المستخدم موجود مسبقاً!")

    # ==================== 2. لوحة التحكم وإضافة البيانات ====================
    def show_dashboard_frame(self):
        self.clear_container()

        # هيدر علوي
        header = tk.Frame(self.main_container, bg="#343a40", height=60)
        header.pack(fill="x", side="top")

        lbl_welcome = tk.Label(
            header,
            text=f"مرحباً، {self.current_user}",
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff",
            bg="#343a40",
        )
        lbl_welcome.pack(side="right", padx=15, pady=15)

        btn_logout = tk.Button(
            header,
            text="خروج",
            font=("Segoe UI", 9, "bold"),
            bg="#dc3545",
            fg="#ffffff",
            bd=0,
            padx=10,
            cursor="hand2",
            command=self.logout_process,
        )
        btn_logout.pack(side="left", padx=15, pady=15)

        # المحتوى الرئيسي
        content = tk.Frame(self.main_container, bg="#f4f6f9", padx=15, pady=15)
        content.pack(fill="both", expand=True)

        # زر الانتقال لشاشة "إضافة بيانات جديدة"
        btn_add_page = tk.Button(
            content,
            text="➕ إضافة بيانات جديدة للنظام",
            font=("Segoe UI", 11, "bold"),
            bg="#007bff",
            fg="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.show_add_data_frame,
        )
        btn_add_page.pack(fill="x", ipady=8, pady=(0, 10))

        # أزرار التعديل والحذف للحساب الشخصي
        manage_frame = tk.Frame(content, bg="#f4f6f9")
        manage_frame.pack(fill="x", pady=(0, 10))

        btn_edit = tk.Button(
            manage_frame,
            text="تعديل حسابي",
            font=("Segoe UI", 9),
            bg="#ffc107",
            fg="#333333",
            bd=0,
            padx=10,
            pady=4,
            command=self.show_edit_frame,
        )
        btn_edit.pack(side="right", padx=2)

        btn_delete = tk.Button(
            manage_frame,
            text="حذف حسابي",
            font=("Segoe UI", 9),
            bg="#dc3545",
            fg="#ffffff",
            bd=0,
            padx=10,
            pady=4,
            command=self.delete_account_process,
        )
        btn_delete.pack(side="left", padx=2)

        # عرض جدول البيانات الخاصة بالمستخدم
        lbl_data_title = tk.Label(
            content,
            text="بياناتك المسجلة:",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6f9",
            anchor="e",
        )
        lbl_data_title.pack(fill="x", pady=(5, 2))

        columns = ("id", "title", "desc", "date")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=8)
        self.tree.heading("id", text="م")
        self.tree.heading("title", text="الاسم ")
        self.tree.heading("desc", text="التشغيل")
        self.tree.heading("date", text="التاريخ")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("title", width=120, anchor="center")
        self.tree.column("desc", width=180, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        # زر لحذف بيان محدد من الجدول
        btn_del_item = tk.Button(
            content,
            text="حذف المختار",
            font=("Segoe UI", 9),
            bg="#6c757d",
            fg="#ffffff",
            bd=0,
            command=self.delete_selected_data_item,
        )
        btn_del_item.pack(anchor="e")

        self.load_user_data()

    def load_user_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, created_at FROM user_data WHERE username = ? ORDER BY id DESC",
            (self.current_user,),
        )
        rows = cursor.fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=r)

    # ==================== 3. شاشة إضافة البيانات الجديدة ====================
    def show_add_data_frame(self):
        self.clear_container()

        frame = tk.Frame(
            self.main_container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=25,
            pady=25,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=440, height=430)
        frame = tk.Frame(
            self.main_container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=25,
            pady=25,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=440, height=430)

        lbl_title = tk.Label(
            frame,
            text="اضافه",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#333333",
        )
        lbl_title.pack(pady=(10, 15))

        lbl_t = tk.Label(
            frame,
            text="اسم المجند",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_t.pack(fill="x", pady=(5, 2))
        self.ent_data_title = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            justify="right",
        )
        self.ent_data_title.pack(fill="x", ipady=4, pady=(0, 10))

        lbl_d = tk.Label(
            frame,
            text=":التشغيل",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_d.pack(fill="x", pady=(5, 2))
        self.ent_data_desc = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            justify="right",
        )
        self.ent_data_desc.pack(fill="x", ipady=4, pady=(0, 20))

        btn_save = tk.Button(
            frame,
            text=" اضافه",
            font=("Segoe UI", 11, "bold"),
            bg="#28a745",
            fg="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.save_new_data,
        )
        btn_save.pack(fill="x", ipady=6, pady=(5, 5))

        btn_back = tk.Button(
            frame,
            text="العودة للوحة التحكم",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6c757d",
            bd=0,
            cursor="hand2",
            command=self.show_dashboard_frame,
        )
        btn_back.pack(pady=5)

    def save_new_data(self):
        title = self.ent_data_title.get().strip()
        desc = self.ent_data_desc.get().strip()

        if not title or not desc:
            messagebox.showwarning("تنبيه", "يرجى ملء جميع حقول البيان!")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_data (username, title, description, created_at) VALUES (?, ?, ?, ?)",
            (self.current_user, title, desc, now),
        )
        conn.commit()
        conn.close()

        log_activity(self.current_user, f"إضافة بيان: {title}")
        messagebox.showinfo("نجاح", "تمت إضافة البيان بنجاح!")
        self.show_dashboard_frame()

    # حذف بيان معين من الجدول
    def delete_selected_data_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تنبيه", "الرجاء اختيار بيان من الجدول لحذفه.")
            return

        item_values = self.tree.item(selected_item, "values")
        item_id = item_values[0]

        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا البيان؟"):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_data WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("تم", "تم حذف البيان بنجاح.")
            self.load_user_data()

    # ==================== تعديل الحساب ====================
    def show_edit_frame(self):
        self.clear_container()
        frame = tk.Frame(
            self.main_container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=25,
            pady=25,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=380)

        lbl_title = tk.Label(
            frame,
            text="تعديل اسم المستخدم",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#333333",
        )
        lbl_title.pack(pady=(10, 20))

        lbl_u = tk.Label(
            frame,
            text="اسم المستخدم الجديد:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            anchor="e",
        )
        lbl_u.pack(fill="x", pady=(5, 2))
        self.ent_new_u = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            justify="right",
        )
        self.ent_new_u.insert(0, self.current_user)
        self.ent_new_u.pack(fill="x", ipady=4, pady=(0, 20))

        btn_save = tk.Button(
            frame,
            text="حفظ التعديل",
            font=("Segoe UI", 11, "bold"),
            bg="#ffc107",
            fg="#333333",
            bd=0,
            command=self.save_account_edit,
        )
        btn_save.pack(fill="x", ipady=6, pady=(5, 5))

        btn_back = tk.Button(
            frame,
            text="رجوع",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6c757d",
            bd=0,
            command=self.show_dashboard_frame,
        )
        btn_back.pack(pady=5)

    def save_account_edit(self):
        new_u = self.ent_new_u.get().strip()
        if not new_u:
            messagebox.showwarning("تنبيه", "الحقل فارغ!")
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET username = ? WHERE username = ?",
                (new_u, self.current_user),
            )
            cursor.execute(
                "UPDATE user_data SET username = ? WHERE username = ?",
                (new_u, self.current_user),
            )
            conn.commit()
            conn.close()
            self.current_user = new_u
            messagebox.showinfo("نجاح", "تم التعديل بنجاح!")
            self.show_dashboard_frame()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "اسم المستخدم موجود مسبقاً!")

    # ==================== حذف الحساب ====================
    def delete_account_process(self):
        if messagebox.askyesno(
            "تحذير",
            "هل تريد حذف حسابك وكل بياناتك نهائياً؟",
            icon="warning",
        ):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (self.current_user,))
            cursor.execute(
                "DELETE FROM user_data WHERE username = ?", (self.current_user,)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("تم", "تم حذف الحساب بنجاح.")
            self.current_user = None
            self.show_login_frame()

    def logout_process(self):
        if messagebox.askyesno("تأكيد", "تسجيل الخروج؟"):
            self.current_user = None
            self.show_login_frame()


if __name__ == "__main__":
    app = FullSystemApp()
    app.mainloop()


import sys
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("company.db")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # جدول الموظفين
        cursor.execute("""CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            salary REAL,
            date_of_appointment TEXT,
            qualification TEXT,
            job TEXT,
            opponent REAL,
            reason TEXT,
            net_salary REAL,
            increases REAL,
            email TEXT,
            phone TEXT
        )""")

        # جدول المخزن
        cursor.execute("""CREATE TABLE IF NOT EXISTS store (
            id_store TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            barcode TEXT UNIQUE,
            price REAL,
            amount INTEGER,
            brand TEXT,
            end_date TEXT,
            company TEXT,
            company_num TEXT,
            resource TEXT,
            resource_num TEXT,
            recipient TEXT,
            recipient_num TEXT
        )""")

        # جدول المنتجات
        cursor.execute("""CREATE TABLE IF NOT EXISTS products (
            products_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            barcode TEXT UNIQUE,
            brand TEXT,
            available_quantity INTEGER,
            required_quantity INTEGER,
            created_at TEXT,
            price REAL,
            company TEXT
        )""")

        self.conn.commit()

    # وظائف الموظفين
    def search_employee(self, key):
        cursor = self.conn.cursor()
        search = f"%{key}%"
        cursor.execute(
            """SELECT * FROM employees WHERE name LIKE ? OR date_of_appointment LIKE ? 
                       OR phone LIKE ? OR id LIKE ?""",
            (search, search, search, search),
        )
        return cursor.fetchall()

    def insert_employee(self, data):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data,
        )
        self.conn.commit()
        return cursor.rowcount

    def update_employee(self, data):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE employees SET name=?, age=?, salary=?, date_of_appointment=?, qualification=?, job=?, opponent=?, reason=?, net_salary=?, increases=?, email=?, phone=? WHERE id=?",
            data,
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_employee(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id=?", (id,))
        self.conn.commit()
        return cursor.rowcount

    def select_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

        cursor.execute("""SELECT COUNT(id), SUM(salary), SUM(opponent), 
                       SUM(increases), SUM(net_salary) FROM employees""")
        stats = cursor.fetchone()
        return employees, stats

    # وظائف المخزن
    def search_store(self, key):
        cursor = self.conn.cursor()
        search = f"%{key}%"
        cursor.execute(
            """SELECT * FROM store 
                       WHERE name LIKE ? OR barcode LIKE ? 
                       OR company LIKE ? OR resource LIKE ? OR recipient LIKE ?""",
            (search, search, search, search, search),
        )
        return cursor.fetchall()

    def insert_store(self, data):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO store VALUES 
                       (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data,
        )
        self.conn.commit()
        return cursor.rowcount

    def update_store(self, data):
        cursor = self.conn.cursor()
        cursor.execute(
            """UPDATE store SET 
                       name=?, barcode=?, price=?, amount=?, brand=?, end_date=?, 
                       company=?, company_num=?, resource=?, resource_num=?, 
                       recipient=?, recipient_num=? WHERE id_store=?""",
            data,
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_store(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM store WHERE id_store=?", (id,))
        self.conn.commit()
        return cursor.rowcount

    def select_store(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM store")
        return cursor.fetchall()

    # وظائف المنتجات
    def search_products(self, key):
        cursor = self.conn.cursor()
        search = f"%{key}%"
        cursor.execute(
            """SELECT * FROM products 
                       WHERE name LIKE ? OR barcode LIKE ? 
                       OR company LIKE ? OR products_id LIKE ? OR brand LIKE ?""",
            (search, search, search, search, search),
        )
        return cursor.fetchall()

    def insert_products(self, data):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO products VALUES 
                       (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data,
        )
        self.conn.commit()
        return cursor.rowcount

    def update_products(self, data):
        cursor = self.conn.cursor()
        cursor.execute(
            """UPDATE products SET 
                       name=?, barcode=?, brand=?, available_quantity=?, 
                       required_quantity=?, created_at=?, price=?, company=?
                       WHERE products_id=?""",
            data,
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_products(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM products WHERE products_id=?", (id,))
        self.conn.commit()
        return cursor.rowcount

    def select_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products")
        return cursor.fetchall()


class HeaderWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setFixedHeight(80)
        layout = QHBoxLayout()

        # استخدام لون بدلاً من صورة غير موجودة
        self.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2c3e50);
            padding: 15px;
            border-radius: 10px;
        """)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white;
            padding: 10px;
        """)

        date_label = QLabel(QDate.currentDate().toString("dddd, d MMMM yyyy"))
        date_label.setStyleSheet("font-size: 16px; color: #ecf0f1;")

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(date_label)

        self.setLayout(layout)


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(200)
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                text-align: left;
                padding: 15px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px 10px;
            }
            QPushButton:hover {
                background-color: #3498db;
                border-left: 4px solid #e74c3c;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 30, 10, 20)
        layout.setSpacing(10)

        title_label = QLabel("MENU")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 15px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.employees_btn = QPushButton("EMPLOYEES")
        self.employees_btn.setCheckable(True)

        self.store_btn = QPushButton("STORE")
        self.store_btn.setCheckable(True)

        self.products_btn = QPushButton("PRODUCTS")
        self.products_btn.setCheckable(True)

        layout.addWidget(self.employees_btn)
        layout.addWidget(self.store_btn)
        layout.addWidget(self.products_btn)
        layout.addStretch()

        self.setLayout(layout)


class EmployeePage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()
        self.setup_connections()

    def setup_connections(self):
        # ربط إشارات الحساب التلقائي
        self.salary_input.valueChanged.connect(self.calculate_net_salary)
        self.opponent_input.valueChanged.connect(self.calculate_net_salary)
        self.increases_input.valueChanged.connect(self.calculate_net_salary)

    def calculate_net_salary(self):
        salary = self.salary_input.value()
        opponent = self.opponent_input.value()
        increases = self.increases_input.value()
        net_salary = salary - opponent + increases
        self.net_salary_input.setValue(net_salary)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        header = HeaderWidget("STAFF MANAGEMENT")
        main_layout.addWidget(header)

        # Create input fields
        input_layout = QGridLayout()
        input_layout.setSpacing(10)

        # Column 1
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter ID")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Name")

        self.age_input = QSpinBox()
        self.age_input.setRange(18, 70)
        self.age_input.setValue(25)

        self.salary_input = QDoubleSpinBox()
        self.salary_input.setRange(0, 100000)
        self.salary_input.setPrefix("EG ")

        self.date_app_input = QDateEdit()
        self.date_app_input.setCalendarPopup(True)
        self.date_app_input.setDate(QDate.currentDate())

        input_layout.addWidget(QLabel("ID:"), 0, 0)
        input_layout.addWidget(self.id_input, 0, 1)
        input_layout.addWidget(QLabel("Name:"), 1, 0)
        input_layout.addWidget(self.name_input, 1, 1)
        input_layout.addWidget(QLabel("Age:"), 2, 0)
        input_layout.addWidget(self.age_input, 2, 1)
        input_layout.addWidget(QLabel("Salary:"), 3, 0)
        input_layout.addWidget(self.salary_input, 3, 1)
        input_layout.addWidget(QLabel("Date:"), 4, 0)
        input_layout.addWidget(self.date_app_input, 4, 1)

        # Column 2
        self.qualification_input = QComboBox()
        self.qualification_input.addItems(
            ["High School", "Diploma", "Bachelor", "Master", "PhD"]
        )

        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Enter Job Title")

        self.opponent_input = QDoubleSpinBox()
        self.opponent_input.setRange(0, 10000)
        self.opponent_input.setPrefix("EG ")

        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Reason for opponent")

        input_layout.addWidget(QLabel("Qualification:"), 0, 2)
        input_layout.addWidget(self.qualification_input, 0, 3)
        input_layout.addWidget(QLabel("Job:"), 1, 2)
        input_layout.addWidget(self.job_input, 1, 3)
        input_layout.addWidget(QLabel("Opponent:"), 2, 2)
        input_layout.addWidget(self.opponent_input, 2, 3)
        input_layout.addWidget(QLabel("Reason:"), 3, 2)
        input_layout.addWidget(self.reason_input, 3, 3)

        # Column 3
        self.increases_input = QDoubleSpinBox()
        self.increases_input.setRange(0, 10000)
        self.increases_input.setPrefix("EG ")

        self.net_salary_input = QDoubleSpinBox()
        self.net_salary_input.setRange(0, 100000)
        self.net_salary_input.setPrefix("EG ")
        self.net_salary_input.setReadOnly(True)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Email")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter Phone")

        input_layout.addWidget(QLabel("Increases:"), 0, 4)
        input_layout.addWidget(self.increases_input, 0, 5)
        input_layout.addWidget(QLabel("Net Salary:"), 1, 4)
        input_layout.addWidget(self.net_salary_input, 1, 5)
        input_layout.addWidget(QLabel("Email:"), 2, 4)
        input_layout.addWidget(self.email_input, 2, 5)
        input_layout.addWidget(QLabel("Phone:"), 3, 4)
        input_layout.addWidget(self.phone_input, 3, 5)

        # Control buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Employee")
        self.add_btn.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px; border-radius: 5px;"
        )

        self.update_btn = QPushButton("Update Employee")
        self.update_btn.setStyleSheet(
            "background-color: #2980b9; color: white; padding: 8px; border-radius: 5px;"
        )

        self.delete_btn = QPushButton("Delete Employee")
        self.delete_btn.setStyleSheet(
            "background-color: #c0392b; color: white; padding: 8px; border-radius: 5px;"
        )

        self.clear_btn = QPushButton("Clear Fields")
        self.clear_btn.setStyleSheet(
            "background-color: #7f8c8d; color: white; padding: 8px; border-radius: 5px;"
        )

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, phone...")
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet(
            "background-color: #16a085; color: white; padding: 8px; border-radius: 5px;"
        )

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        headers = [
            "ID",
            "Name",
            "Age",
            "Salary",
            "Date",
            "Qualification",
            "Job",
            "Opponent",
            "Reason",
            "Net Salary",
            "Increases",
            "Email",
            "Phone",
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        # Statistics
        stats_layout = QHBoxLayout()

        self.total_label = QLabel("0")
        self.total_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )

        self.salary_label = QLabel("EG 0.00")
        self.salary_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #27ae60;"
        )

        self.opponent_label = QLabel("EG 0.00")
        self.opponent_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #c0392b;"
        )

        self.increases_label = QLabel("EG 0.00")
        self.increases_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #16a085;"
        )

        self.net_label = QLabel("EG 0.00")
        self.net_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2980b9;"
        )

        stats_layout.addWidget(QLabel("Total Employees:"))
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(QLabel("Total Salary:"))
        stats_layout.addWidget(self.salary_label)
        stats_layout.addWidget(QLabel("Total Opponent:"))
        stats_layout.addWidget(self.opponent_label)
        stats_layout.addWidget(QLabel("Total Increases:"))
        stats_layout.addWidget(self.increases_label)
        stats_layout.addWidget(QLabel("Total Net Salary:"))
        stats_layout.addWidget(self.net_label)
        stats_layout.addStretch()

        # Add all to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table, 1)
        main_layout.addLayout(stats_layout)

        self.setLayout(main_layout)

        # Connect signals
        self.add_btn.clicked.connect(self.add_employee)
        self.update_btn.clicked.connect(self.update_employee)
        self.delete_btn.clicked.connect(self.delete_employee)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.search_btn.clicked.connect(self.search_employee)
        self.table.itemSelectionChanged.connect(self.load_selected_employee)

    def load_data(self):
        employees, stats = self.db.select_employees()
        self.table.setRowCount(len(employees))

        for row_idx, employee in enumerate(employees):
            for col_idx, value in enumerate(employee):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

        # Update statistics
        if stats:
            self.total_label.setText(str(stats[0] or 0))
            self.salary_label.setText(f"EG{stats[1] or 0:,.2f}")
            self.opponent_label.setText(f"EG{stats[2] or 0:,.2f}")
            self.increases_label.setText(f"EG{stats[3] or 0:,.2f}")
            self.net_label.setText(f"EG{stats[4] or 0:,.2f}")

    def load_selected_employee(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.id_input.setText(self.table.item(row, 0).text())
            self.name_input.setText(self.table.item(row, 1).text())
            self.age_input.setValue(int(self.table.item(row, 2).text() or 0))
            self.salary_input.setValue(float(self.table.item(row, 3).text() or 0))

            date_str = self.table.item(row, 4).text()
            if date_str:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.date_app_input.setDate(date)

            self.qualification_input.setCurrentText(self.table.item(row, 5).text())
            self.job_input.setText(self.table.item(row, 6).text())
            self.opponent_input.setValue(float(self.table.item(row, 7).text() or 0))
            self.reason_input.setText(self.table.item(row, 8).text())
            self.net_salary_input.setValue(float(self.table.item(row, 9).text() or 0))
            self.increases_input.setValue(float(self.table.item(row, 10).text() or 0))
            self.email_input.setText(self.table.item(row, 11).text())
            self.phone_input.setText(self.table.item(row, 12).text())

    def clear_fields(self):
        self.id_input.clear()
        self.name_input.clear()
        self.age_input.setValue(25)
        self.salary_input.setValue(0)
        self.date_app_input.setDate(QDate.currentDate())
        self.qualification_input.setCurrentIndex(0)
        self.job_input.clear()
        self.opponent_input.setValue(0)
        self.reason_input.clear()
        self.net_salary_input.setValue(0)
        self.increases_input.setValue(0)
        self.email_input.clear()
        self.phone_input.clear()
        self.table.clearSelection()

    def add_employee(self):
        if not self.id_input.text() or not self.name_input.text():
            QMessageBox.warning(self, "Error", "Please enter ID and Name")
            return

        data = (
            self.id_input.text(),
            self.name_input.text(),
            self.age_input.value(),
            self.salary_input.value(),
            self.date_app_input.date().toString("yyyy-MM-dd"),
            self.qualification_input.currentText(),
            self.job_input.text(),
            self.opponent_input.value(),
            self.reason_input.text(),
            self.net_salary_input.value(),
            self.increases_input.value(),
            self.email_input.text(),
            self.phone_input.text(),
        )

        try:
            if self.db.insert_employee(data) > 0:
                QMessageBox.information(self, "Success", "Employee added successfully")
                self.load_data()
                self.clear_fields()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "ID already exists")

    def update_employee(self):
        if not self.id_input.text():
            QMessageBox.warning(self, "Warning", "Please select an employee to update")
            return

        data = (
            self.name_input.text(),
            self.age_input.value(),
            self.salary_input.value(),
            self.date_app_input.date().toString("yyyy-MM-dd"),
            self.qualification_input.currentText(),
            self.job_input.text(),
            self.opponent_input.value(),
            self.reason_input.text(),
            self.net_salary_input.value(),
            self.increases_input.value(),
            self.email_input.text(),
            self.phone_input.text(),
            self.id_input.text(),
        )

        if self.db.update_employee(data) > 0:
            QMessageBox.information(self, "Success", "Employee updated successfully")
            self.load_data()
        else:
            QMessageBox.warning(self, "Error", "Failed to update employee")

    def delete_employee(self):
        id = self.id_input.text()
        if not id:
            QMessageBox.warning(self, "Warning", "Please select an employee to delete")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to delete this employee?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_employee(id) > 0:
                QMessageBox.information(
                    self, "Success", "Employee deleted successfully"
                )
                self.load_data()
                self.clear_fields()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete employee")

    def search_employee(self):
        key = self.search_input.text()
        if not key:
            self.load_data()
            return

        results = self.db.search_employee(key)
        self.table.setRowCount(len(results))

        for row_idx, employee in enumerate(results):
            for col_idx, value in enumerate(employee):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


class StorePage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        header = HeaderWidget("STORE MANAGEMENT")
        main_layout.addWidget(header)

        # Create input layout
        input_layout = QGridLayout()
        input_layout.setSpacing(10)

        # Input fields
        self.id_store_input = QLineEdit()
        self.name_input = QLineEdit()
        self.barcode_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setPrefix("EG ")

        self.amount_input = QSpinBox()
        self.amount_input.setRange(0, 1000000)

        self.brand_input = QComboBox()
        self.brand_input.addItems(["Mobile", "Headphones", "Accessories", "Other"])

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate().addMonths(6))

        self.company_input = QLineEdit()
        self.company_num_input = QLineEdit()
        self.resource_input = QLineEdit()
        self.resource_num_input = QLineEdit()
        self.recipient_input = QLineEdit()
        self.recipient_num_input = QLineEdit()

        # Add to layout
        input_layout.addWidget(QLabel("Store ID:"), 0, 0)
        input_layout.addWidget(self.id_store_input, 0, 1)
        input_layout.addWidget(QLabel("Name:"), 1, 0)
        input_layout.addWidget(self.name_input, 1, 1)
        input_layout.addWidget(QLabel("Barcode:"), 2, 0)
        input_layout.addWidget(self.barcode_input, 2, 1)
        input_layout.addWidget(QLabel("Price:"), 3, 0)
        input_layout.addWidget(self.price_input, 3, 1)

        input_layout.addWidget(QLabel("Amount:"), 0, 2)
        input_layout.addWidget(self.amount_input, 0, 3)
        input_layout.addWidget(QLabel("Brand:"), 1, 2)
        input_layout.addWidget(self.brand_input, 1, 3)
        input_layout.addWidget(QLabel("End Date:"), 2, 2)
        input_layout.addWidget(self.end_date_input, 2, 3)
        input_layout.addWidget(QLabel("Company:"), 3, 2)
        input_layout.addWidget(self.company_input, 3, 3)

        input_layout.addWidget(QLabel("Company Number:"), 0, 4)
        input_layout.addWidget(self.company_num_input, 0, 5)
        input_layout.addWidget(QLabel("Resource:"), 1, 4)
        input_layout.addWidget(self.resource_input, 1, 5)
        input_layout.addWidget(QLabel("Resource Number:"), 2, 4)
        input_layout.addWidget(self.resource_num_input, 2, 5)
        input_layout.addWidget(QLabel("Recipient:"), 3, 4)
        input_layout.addWidget(self.recipient_input, 3, 5)
        input_layout.addWidget(QLabel("Recipient Number:"), 4, 4)
        input_layout.addWidget(self.recipient_num_input, 4, 5)

        # Control buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Item")
        self.add_btn.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px; border-radius: 5px;"
        )

        self.update_btn = QPushButton("Update Item")
        self.update_btn.setStyleSheet(
            "background-color: #2980b9; color: white; padding: 8px; border-radius: 5px;"
        )

        self.delete_btn = QPushButton("Delete Item")
        self.delete_btn.setStyleSheet(
            "background-color: #c0392b; color: white; padding: 8px; border-radius: 5px;"
        )

        self.clear_btn = QPushButton("Clear Fields")
        self.clear_btn.setStyleSheet(
            "background-color: #7f8c8d; color: white; padding: 8px; border-radius: 5px;"
        )

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet(
            "background-color: #16a085; color: white; padding: 8px; border-radius: 5px;"
        )

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        headers = [
            "ID",
            "Name",
            "Barcode",
            "Price",
            "Amount",
            "Brand",
            "End Date",
            "Company",
            "Company Number",
            "Resource",
            "Resource Number",
            "Recipient",
            "Recipient Number",
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        # Add to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table, 1)

        self.setLayout(main_layout)

        # Connect signals
        self.add_btn.clicked.connect(self.add_store)
        self.update_btn.clicked.connect(self.update_store)
        self.delete_btn.clicked.connect(self.delete_store)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.search_btn.clicked.connect(self.search_store)
        self.table.itemSelectionChanged.connect(self.load_selected_store)

    def load_data(self):
        store_items = self.db.select_store()
        self.table.setRowCount(len(store_items))

        for row_idx, item in enumerate(store_items):
            for col_idx, value in enumerate(item):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def load_selected_store(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.id_store_input.setText(self.table.item(row, 0).text())
            self.name_input.setText(self.table.item(row, 1).text())
            self.barcode_input.setText(self.table.item(row, 2).text())
            self.price_input.setValue(float(self.table.item(row, 3).text() or 0))
            self.amount_input.setValue(int(self.table.item(row, 4).text() or 0))
            self.brand_input.setCurrentText(self.table.item(row, 5).text())

            date_str = self.table.item(row, 6).text()
            if date_str:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.end_date_input.setDate(date)

            self.company_input.setText(self.table.item(row, 7).text())
            self.company_num_input.setText(self.table.item(row, 8).text())
            self.resource_input.setText(self.table.item(row, 9).text())
            self.resource_num_input.setText(self.table.item(row, 10).text())
            self.recipient_input.setText(self.table.item(row, 11).text())
            self.recipient_num_input.setText(self.table.item(row, 12).text())

    def clear_fields(self):
        self.id_store_input.clear()
        self.name_input.clear()
        self.barcode_input.clear()
        self.price_input.setValue(0)
        self.amount_input.setValue(0)
        self.brand_input.setCurrentIndex(0)
        self.end_date_input.setDate(QDate.currentDate().addMonths(6))
        self.company_input.clear()
        self.company_num_input.clear()
        self.resource_input.clear()
        self.resource_num_input.clear()
        self.recipient_input.clear()
        self.recipient_num_input.clear()
        self.table.clearSelection()

    def add_store(self):
        if not self.id_store_input.text() or not self.name_input.text():
            QMessageBox.warning(self, "Error", "Please enter Store ID and Name")
            return

        data = (
            self.id_store_input.text(),
            self.name_input.text(),
            self.barcode_input.text(),
            self.price_input.value(),
            self.amount_input.value(),
            self.brand_input.currentText(),
            self.end_date_input.date().toString("yyyy-MM-dd"),
            self.company_input.text(),
            self.company_num_input.text(),
            self.resource_input.text(),
            self.resource_num_input.text(),
            self.recipient_input.text(),
            self.recipient_num_input.text(),
        )

        try:
            if self.db.insert_store(data) > 0:
                QMessageBox.information(
                    self, "Success", "Store item added successfully"
                )
                self.load_data()
                self.clear_fields()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Store ID or Barcode already exists")

    def update_store(self):
        if not self.id_store_input.text():
            QMessageBox.warning(self, "Warning", "Please select an item to update")
            return

        data = (
            self.name_input.text(),
            self.barcode_input.text(),
            self.price_input.value(),
            self.amount_input.value(),
            self.brand_input.currentText(),
            self.end_date_input.date().toString("yyyy-MM-dd"),
            self.company_input.text(),
            self.company_num_input.text(),
            self.resource_input.text(),
            self.resource_num_input.text(),
            self.recipient_input.text(),
            self.recipient_num_input.text(),
            self.id_store_input.text(),
        )

        if self.db.update_store(data) > 0:
            QMessageBox.information(self, "Success", "Store item updated successfully")
            self.load_data()
        else:
            QMessageBox.warning(self, "Error", "Failed to update store item")

    def delete_store(self):
        id = self.id_store_input.text()
        if not id:
            QMessageBox.warning(self, "Warning", "Please select an item to delete")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_store(id) > 0:
                QMessageBox.information(
                    self, "Success", "Store item deleted successfully"
                )
                self.load_data()
                self.clear_fields()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete store item")

    def search_store(self):
        key = self.search_input.text()
        if not key:
            self.load_data()
            return

        results = self.db.search_store(key)
        self.table.setRowCount(len(results))

        for row_idx, item in enumerate(results):
            for col_idx, value in enumerate(item):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


class ProductsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        header = HeaderWidget("PRODUCTS MANAGEMENT")
        main_layout.addWidget(header)

        # Create input layout
        input_layout = QGridLayout()
        input_layout.setSpacing(10)

        # Input fields
        self.products_id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.barcode_input = QLineEdit()
        self.brand_input = QComboBox()
        self.brand_input.addItems(["Phone", "Headphones", "Accessories", "Other"])

        self.available_quantity_input = QSpinBox()
        self.available_quantity_input.setRange(0, 1000000)

        self.required_quantity_input = QSpinBox()
        self.required_quantity_input.setRange(0, 1000000)

        self.created_at_input = QDateEdit()
        self.created_at_input.setCalendarPopup(True)
        self.created_at_input.setDate(QDate.currentDate())

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setPrefix("EG ")

        self.company_input = QLineEdit()

        # Add to layout
        input_layout.addWidget(QLabel("Product ID:"), 0, 0)
        input_layout.addWidget(self.products_id_input, 0, 1)
        input_layout.addWidget(QLabel("Name:"), 1, 0)
        input_layout.addWidget(self.name_input, 1, 1)
        input_layout.addWidget(QLabel("Barcode:"), 2, 0)
        input_layout.addWidget(self.barcode_input, 2, 1)
        input_layout.addWidget(QLabel("Brand:"), 3, 0)
        input_layout.addWidget(self.brand_input, 3, 1)

        input_layout.addWidget(QLabel("Available Quantity:"), 0, 2)
        input_layout.addWidget(self.available_quantity_input, 0, 3)
        input_layout.addWidget(QLabel("Required Quantity:"), 1, 2)
        input_layout.addWidget(self.required_quantity_input, 1, 3)
        input_layout.addWidget(QLabel("Created At:"), 2, 2)
        input_layout.addWidget(self.created_at_input, 2, 3)
        input_layout.addWidget(QLabel("Price:"), 3, 2)
        input_layout.addWidget(self.price_input, 3, 3)

        input_layout.addWidget(QLabel("Company:"), 0, 4)
        input_layout.addWidget(self.company_input, 0, 5)

        # Control buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Product")
        self.add_btn.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px; border-radius: 5px;"
        )

        self.update_btn = QPushButton("Update Product")
        self.update_btn.setStyleSheet(
            "background-color: #2980b9; color: white; padding: 8px; border-radius: 5px;"
        )

        self.delete_btn = QPushButton("Delete Product")
        self.delete_btn.setStyleSheet(
            "background-color: #c0392b; color: white; padding: 8px; border-radius: 5px;"
        )

        self.clear_btn = QPushButton("Clear Fields")
        self.clear_btn.setStyleSheet(
            "background-color: #7f8c8d; color: white; padding: 8px; border-radius: 5px;"
        )

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet(
            "background-color: #16a085; color: white; padding: 8px; border-radius: 5px;"
        )

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        headers = [
            "ID",
            "Name",
            "Barcode",
            "Brand",
            "Available Quantity",
            "Required Quantity",
            "Created At",
            "Price",
            "Company",
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        # Add to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table, 1)

        self.setLayout(main_layout)

        # Connect signals
        self.add_btn.clicked.connect(self.add_product)
        self.update_btn.clicked.connect(self.update_product)
        self.delete_btn.clicked.connect(self.delete_product)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.search_btn.clicked.connect(self.search_products)
        self.table.itemSelectionChanged.connect(self.load_selected_product)

    def load_data(self):
        products = self.db.select_products()
        self.table.setRowCount(len(products))

        for row_idx, product in enumerate(products):
            for col_idx, value in enumerate(product):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def load_selected_product(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.products_id_input.setText(self.table.item(row, 0).text())
            self.name_input.setText(self.table.item(row, 1).text())
            self.barcode_input.setText(self.table.item(row, 2).text())
            self.brand_input.setCurrentText(self.table.item(row, 3).text())
            self.available_quantity_input.setValue(
                int(self.table.item(row, 4).text() or 0)
            )
            self.required_quantity_input.setValue(
                int(self.table.item(row, 5).text() or 0)
            )

            date_str = self.table.item(row, 6).text()
            if date_str:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.created_at_input.setDate(date)

            self.price_input.setValue(float(self.table.item(row, 7).text() or 0))
            self.company_input.setText(self.table.item(row, 8).text())

    def clear_fields(self):
        self.products_id_input.clear()
        self.name_input.clear()
        self.barcode_input.clear()
        self.brand_input.setCurrentIndex(0)
        self.available_quantity_input.setValue(0)
        self.required_quantity_input.setValue(0)
        self.created_at_input.setDate(QDate.currentDate())
        self.price_input.setValue(0)
        self.company_input.clear()
        self.table.clearSelection()

    def add_product(self):
        if not self.products_id_input.text() or not self.name_input.text():
            QMessageBox.warning(self, "Error", "Please enter Product ID and Name")
            return

        data = (
            self.products_id_input.text(),
            self.name_input.text(),
            self.barcode_input.text(),
            self.brand_input.currentText(),
            self.available_quantity_input.value(),
            self.required_quantity_input.value(),
            self.created_at_input.date().toString("yyyy-MM-dd"),
            self.price_input.value(),
            self.company_input.text(),
        )

        try:
            if self.db.insert_products(data) > 0:
                QMessageBox.information(self, "Success", "Product added successfully")
                self.load_data()
                self.clear_fields()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Product ID or Barcode already exists")

    def update_product(self):
        if not self.products_id_input.text():
            QMessageBox.warning(self, "Warning", "Please select a product to update")
            return

        data = (
            self.name_input.text(),
            self.barcode_input.text(),
            self.brand_input.currentText(),
            self.available_quantity_input.value(),
            self.required_quantity_input.value(),
            self.created_at_input.date().toString("yyyy-MM-dd"),
            self.price_input.value(),
            self.company_input.text(),
            self.products_id_input.text(),
        )

        if self.db.update_products(data) > 0:
            QMessageBox.information(self, "Success", "Product updated successfully")
            self.load_data()
        else:
            QMessageBox.warning(self, "Error", "Failed to update product")

    def delete_product(self):
        id = self.products_id_input.text()
        if not id:
            QMessageBox.warning(self, "Warning", "Please select a product to delete")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_products(id) > 0:
                QMessageBox.information(self, "Success", "Product deleted successfully")
                self.load_data()
                self.clear_fields()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete product")

    def search_products(self):
        key = self.search_input.text()
        if not key:
            self.load_data()
            return

        results = self.db.search_products(key)
        self.table.setRowCount(len(results))

        for row_idx, product in enumerate(results):
            for col_idx, value in enumerate(product):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP Management System")
        self.setGeometry(100, 100, 1400, 800)
        self.db = Database()

        # Create sidebar and pages
        self.sidebar = Sidebar()
        self.employee_page = EmployeePage(self.db)
        self.store_page = StorePage(self.db)
        self.products_page = ProductsPage(self.db)

        # Create stacked widget
        self.stack = QStackedWidget()
        self.stack.addWidget(self.employee_page)
        self.stack.addWidget(self.store_page)
        self.stack.addWidget(self.products_page)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect sidebar buttons
        self.sidebar.employees_btn.clicked.connect(lambda: self.switch_page(0))
        self.sidebar.store_btn.clicked.connect(lambda: self.switch_page(1))
        self.sidebar.products_btn.clicked.connect(lambda: self.switch_page(2))

        # Set initial page
        self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        # Update button states
        self.sidebar.employees_btn.setChecked(index == 0)
        self.sidebar.store_btn.setChecked(index == 1)
        self.sidebar.products_btn.setChecked(index == 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
