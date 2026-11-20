import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookings.db")
BG = "#F4F6FA"
NAVY = "#24364B"
WHITE = "#FFFFFF"
BLACK = "#222222"
GREY = "#687386"
PALE = "#E8EDF3"

TABLES = {
    "users": {
        "title": "Customers",
        "pk": "user_id",
        "columns": ["user_id", "name", "email", "phone"],
        "labels": ["Customer ID", "Name", "Email", "Phone"],
        "editable": ["name", "email", "phone"],
        "required": ["name", "email", "phone"],
        "types": {"name": "text", "email": "email", "phone": "text"}
    },
    "available_dates": {
        "title": "Available Dates & Services",
        "pk": "date_id",
        "columns": ["date_id", "service_name", "booking_date", "time_slot", "price"],
        "labels": ["Date ID", "Service", "Date (YYYY-MM-DD)", "Time Slot", "Price"],
        "editable": ["service_name", "booking_date", "time_slot", "price"],
        "required": ["service_name", "booking_date", "time_slot", "price"],
        "types": {"service_name": "text", "booking_date": "date", "time_slot": "text", "price": "number"}
    },
    "bookings": {
        "title": "Bookings",
        "pk": "booking_id",
        "columns": ["booking_id", "user_id", "date_id", "guests", "total_price"],
        "labels": ["Booking ID", "Customer ID", "Available Date ID", "Guests", "Total Price"],
        "editable": ["user_id", "date_id", "guests", "total_price"],
        "required": ["user_id", "date_id", "guests", "total_price"],
        "types": {"user_id": "integer", "date_id": "integer", "guests": "positive_integer", "total_price": "number"}
    }
}


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def setup_database():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS available_dates (
                date_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date_id INTEGER NOT NULL,
                guests INTEGER NOT NULL CHECK(guests > 0),
                total_price REAL NOT NULL CHECK(total_price >= 0),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(date_id) REFERENCES available_dates(date_id)
            )
        """)
        user_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            cursor.executemany(
                "INSERT INTO users(name,email,phone) VALUES(?,?,?)",
                [
                    ("Anna Kovacs", "anna@gmail.com", "06201234567"),
                    ("Bence Nagy", "bence@gmail.com", "06307654321"),
                    ("Sara Toth", "sara@gmail.com", "06701112233")
                ]
            )
        date_count = cursor.execute("SELECT COUNT(*) FROM available_dates").fetchone()[0]
        if date_count == 0:
            cursor.executemany(
                "INSERT INTO available_dates(service_name,booking_date,time_slot,price) VALUES(?,?,?,?)",
                [
                    ("Tennis Court", "2026-11-25", "10:00-11:00", 20.0),
                    ("Meeting Room", "2026-11-25", "14:00-16:00", 50.0),
                    ("Spa Session", "2026-11-26", "12:00-13:00", 30.0)
                ]
            )


class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Booking Management System")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)
        self.windows = {}
        self.configure_styles()
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.root, bg=NAVY)
        self.welcome_frame.pack(fill="both", expand=True)
        self.welcome_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "welcome.png")
        self.welcome_original = None
        self.welcome_photo = None
        self.welcome_label = tk.Label(self.welcome_frame, bg=NAVY)
        self.welcome_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        if os.path.exists(self.welcome_image_path):
            try:
                self.welcome_original = Image.open(self.welcome_image_path).convert("RGB")
                self.root.bind("<Configure>", self.resize_welcome_image)
                self.root.after(100, self.resize_welcome_image)
            except Exception as error:
                self.welcome_label.configure(
                    text=f"WELCOME\n\nCould not load welcome.png: {error}",
                    fg=WHITE, font=("Arial", 18, "bold")
                )
        else:
            self.welcome_label.configure(
                text="BOOKING MANAGEMENT SYSTEM\n\nMeeting Room  •  Tennis Court  •  Spa",
                fg=WHITE, font=("Arial", 22, "bold")
            )
        self.enter_button = tk.Button(
            self.welcome_frame, text="ENTER", command=self.enter_application,
            bg=WHITE, fg=BLACK, activebackground=PALE, activeforeground=NAVY,
            relief="solid", bd=2, padx=35, pady=13,
            font=("Arial", 13, "bold"), cursor="hand2"
        )
        self.enter_button.place(relx=0.5, rely=0.82, anchor="center")
        self.enter_button.lift()

    def resize_welcome_image(self, event=None):
        if self.welcome_original is None or not self.welcome_frame.winfo_exists():
            return
        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)
        source_width, source_height = self.welcome_original.size
        scale = max(width / source_width, height / source_height)
        new_size = (int(source_width * scale), int(source_height * scale))
        resized = self.welcome_original.resize(new_size, Image.Resampling.LANCZOS)
        left = max((new_size[0] - width) // 2, 0)
        top = max((new_size[1] - height) // 2, 0)
        resized = resized.crop((left, top, left + width, top + height))
        self.welcome_photo = ImageTk.PhotoImage(resized)
        self.welcome_label.configure(image=self.welcome_photo)
        self.welcome_label.lower()
        self.enter_button.lift()

    def enter_application(self):
        self.root.unbind("<Configure>")
        self.welcome_frame.destroy()
        self.build_main_window()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, foreground=BLACK, rowheight=29,
                        fieldbackground=WHITE, font=("Arial", 10))
        style.configure("Treeview.Heading", background=PALE, foreground=NAVY,
                        font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", NAVY)], foreground=[("selected", WHITE)])
        style.configure("TCombobox", padding=5)

    def button(self, parent, text, command, primary=False):
        return tk.Button(
            parent, text=text, command=command, bg=WHITE, fg=BLACK,
            activebackground=PALE, activeforeground=NAVY, relief="solid",
            bd=1, padx=13, pady=8, font=("Arial", 10, "bold"),
            cursor="hand2", highlightthickness=0
        )

    def build_main_window(self):
        header = tk.Frame(self.root, bg=NAVY, padx=30, pady=28)
        header.pack(fill="x")
        tk.Label(header, text="BOOKING MANAGEMENT SYSTEM", bg=NAVY, fg=WHITE,
                 font=("Arial", 23, "bold")).pack(anchor="w")
        tk.Label(header, text="Manage customers, services, bookings and reports",
                 bg=NAVY, fg=WHITE, font=("Arial", 11)).pack(anchor="w", pady=(7, 0))

        content = tk.Frame(self.root, bg=BG, padx=35, pady=30)
        content.pack(fill="both", expand=True)
        tk.Label(content, text="Welcome", bg=BG, fg=NAVY,
                 font=("Arial", 21, "bold")).pack(anchor="w")
        tk.Label(content, text="Choose a section from the menu below.",
                 bg=BG, fg=GREY, font=("Arial", 11)).pack(anchor="w", pady=(5, 22))

        menu = tk.Frame(content, bg=BG)
        menu.pack(fill="x")
        options = [
            ("Customers", "Manage customer records", lambda: self.open_table("users")),
            ("Available Dates & Services", "Manage dates, time slots and prices",
             lambda: self.open_table("available_dates")),
            ("Bookings", "Create, edit and cancel bookings", lambda: self.open_table("bookings")),
            ("Reports", "View booking statistics and charts", self.open_reports)
        ]
        for index, (heading, description, action) in enumerate(options):
            card = tk.Frame(menu, bg=WHITE, bd=1, relief="solid", padx=18, pady=18)
            card.grid(row=index // 2, column=index % 2, sticky="nsew",
                      padx=8, pady=8)
            tk.Label(card, text=heading, bg=WHITE, fg=NAVY,
                     font=("Arial", 14, "bold")).pack(anchor="w")
            tk.Label(card, text=description, bg=WHITE, fg=GREY,
                     font=("Arial", 10)).pack(anchor="w", pady=(6, 15))
            self.button(card, "Open " + heading, action).pack(anchor="w")
        menu.columnconfigure(0, weight=1)
        menu.columnconfigure(1, weight=1)
        footer = tk.Frame(self.root, bg=BG, padx=35, pady=12)
        footer.pack(fill="x")
        self.button(footer, "Exit", self.root.destroy).pack(side="right")

    def open_window(self, key, title, geometry="1100x680"):
        existing = self.windows.get(key)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_force()
            return None
        window = tk.Toplevel(self.root)
        self.windows[key] = window
        window.title(title)
        window.geometry(geometry)
        window.configure(bg=BG)
        window.transient(self.root)
        return window

    def fetch_rows(self, table):
        config = TABLES[table]
        with get_connection() as connection:
            return connection.execute(
                f"SELECT {','.join(config['columns'])} FROM {table} ORDER BY {config['pk']}"
            ).fetchall()

    def open_table(self, table):
        config = TABLES[table]
        win = self.open_window("table_" + table, config["title"], "1150x700")
        if win is None:
            return
        container = tk.Frame(win, bg=BG, padx=18, pady=16)
        container.pack(fill="both", expand=True)
        top = tk.Frame(container, bg=BG)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text=config["title"], bg=BG, fg=NAVY,
                 font=("Arial", 19, "bold")).pack(side="left")
        controls = tk.Frame(container, bg=BG)
        controls.pack(fill="x", pady=(0, 12))
        self.button(controls, "Add New", lambda: self.edit_record(table)).pack(side="left", padx=(0, 7))
        self.button(controls, "Edit Selected", lambda: self.edit_selected(table, tree)).pack(side="left", padx=7)
        self.button(controls, "Delete Selected", lambda: self.delete_selected(table, tree)).pack(side="left", padx=7)
        self.button(controls, "Show Related Records", lambda: self.show_related(table, tree)).pack(side="left", padx=7)
        self.button(controls, "Refresh", lambda: self.refresh_table(table, tree)).pack(side="left", padx=7)
        self.button(controls, "Import CSV/Excel", lambda: self.import_rows(table, tree)).pack(side="right", padx=(7, 0))
        self.button(controls, "Export CSV/Excel", lambda: self.export_rows(table)).pack(side="right", padx=7)

        tree_frame = tk.Frame(container, bg=WHITE, bd=1, relief="solid")
        tree_frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(tree_frame, columns=config["columns"], show="headings", selectmode="browse")
        for column, label in zip(config["columns"], config["labels"]):
            tree.heading(column, text=label)
            tree.column(column, width=150, minwidth=90, anchor="center")
        vertical = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.refresh_table(table, tree)
        tree.bind("<Double-1>", lambda event: self.edit_selected(table, tree))

    def refresh_table(self, table, tree):
        for item in tree.get_children():
            tree.delete(item)
        for row in self.fetch_rows(table):
            tree.insert("", "end", iid=str(row[0]), values=row)

    def selected_id(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a row first.")
            return None
        return int(selected[0])

    def edit_selected(self, table, tree):
        record_id = self.selected_id(tree)
        if record_id is not None:
            self.edit_record(table, record_id)

    def edit_record(self, table, record_id=None):
        config = TABLES[table]
        title = "Edit " if record_id is not None else "Add "
        win = tk.Toplevel(self.root)
        win.title(title + config["title"])
        win.geometry("480x560")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        body = tk.Frame(win, bg=WHITE, padx=24, pady=20, bd=1, relief="solid")
        body.pack(fill="both", expand=True, padx=18, pady=18)
        tk.Label(body, text=title + config["title"], bg=WHITE, fg=NAVY,
                 font=("Arial", 17, "bold")).pack(anchor="w", pady=(0, 15))
        entries = {}
        current = None
        if record_id is not None:
            with get_connection() as connection:
                current = connection.execute(
                    f"SELECT {','.join(config['columns'])} FROM {table} WHERE {config['pk']}=?",
                    (record_id,)
                ).fetchone()
        for field, label in zip(config["editable"], [config["labels"][config["columns"].index(x)] for x in config["editable"]]):
            tk.Label(body, text=label, bg=WHITE, fg=NAVY,
                     font=("Arial", 10, "bold")).pack(anchor="w", pady=(7, 2))
            if table == "bookings" and field == "user_id":
                values = self.lookup_values("users")
                widget = ttk.Combobox(body, values=[f"{r[0]} - {r[1]}" for r in values], state="readonly")
                if current:
                    match = next((f"{r[0]} - {r[1]}" for r in values if r[0] == current[1]), "")
                    widget.set(match)
            elif table == "bookings" and field == "date_id":
                values = self.lookup_values("available_dates")
                widget = ttk.Combobox(body, values=[f"{r[0]} - {r[1]} | {r[2]} | {r[3]} | ${r[4]:.2f}" for r in values], state="readonly")
                if current:
                    match = next((f"{r[0]} - {r[1]} | {r[2]} | {r[3]} | ${r[4]:.2f}" for r in values if r[0] == current[2]), "")
                    widget.set(match)
            else:
                widget = tk.Entry(body, font=("Arial", 11), relief="solid", bd=1)
                if current:
                    value = current[config["columns"].index(field)]
                    widget.insert(0, str(value))
                elif table == "bookings" and field == "guests":
                    widget.insert(0, "1")
            widget.pack(fill="x", ipady=5, pady=(0, 3))
            entries[field] = widget

        def save():
            try:
                values = {}
                for field, widget in entries.items():
                    raw = widget.get().strip()
                    if table == "bookings" and field in ("user_id", "date_id"):
                        if not raw:
                            raise ValueError("Please select " + field.replace("_", " ") + ".")
                        values[field] = int(raw.split(" - ", 1)[0])
                    else:
                        values[field] = self.validate_value(field, raw, config["types"][field])
                if table == "bookings":
                    with get_connection() as connection:
                        service_price = connection.execute(
                            "SELECT price FROM available_dates WHERE date_id=?", (values["date_id"],)
                        ).fetchone()
                    if service_price is None:
                        raise ValueError("The selected service does not exist.")
                    values["total_price"] = round(values["guests"] * float(service_price[0]), 2)
                if record_id is None:
                    fields = list(values)
                    placeholders = ",".join("?" for _ in fields)
                    with get_connection() as connection:
                        connection.execute(
                            f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})",
                            [values[field] for field in fields]
                        )
                else:
                    fields = list(values)
                    assignments = ",".join(f"{field}=?" for field in fields)
                    with get_connection() as connection:
                        connection.execute(
                            f"UPDATE {table} SET {assignments} WHERE {config['pk']}=?",
                            [values[field] for field in fields] + [record_id]
                        )
                messagebox.showinfo("Saved", "The record has been saved successfully.")
                win.destroy()
                self.refresh_all_open_tables()
            except (ValueError, sqlite3.IntegrityError) as error:
                messagebox.showerror("Validation Error", str(error))

        self.button(body, "Save", save).pack(anchor="e", pady=(18, 0))

    def lookup_values(self, table):
        if table == "users":
            query = "SELECT user_id,name FROM users ORDER BY name"
        else:
            query = "SELECT date_id,service_name,booking_date,time_slot,price FROM available_dates ORDER BY booking_date"
        with get_connection() as connection:
            return connection.execute(query).fetchall()

    def validate_value(self, field, value, value_type):
        if not value:
            raise ValueError(f"{field.replace('_', ' ').capitalize()} is required.")
        if value_type == "number":
            try:
                number = float(value)
            except ValueError:
                raise ValueError(f"{field.replace('_', ' ').capitalize()} must be numeric.")
            if number < 0:
                raise ValueError(f"{field.replace('_', ' ').capitalize()} cannot be negative.")
            return number
        if value_type == "integer":
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"{field.replace('_', ' ').capitalize()} must be a whole number.")
        if value_type == "positive_integer":
            try:
                number = int(value)
            except ValueError:
                raise ValueError("Guests must be a whole number.")
            if number <= 0:
                raise ValueError("Guests must be greater than zero.")
            return number
        if value_type == "date":
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must use YYYY-MM-DD format.")
            return value
        if value_type == "email" and ("@" not in value or "." not in value.split("@")[-1]):
            raise ValueError("Enter a valid email address.")
        return value

    def delete_selected(self, table, tree):
        record_id = self.selected_id(tree)
        if record_id is None:
            return
        config = TABLES[table]
        if not messagebox.askyesno("Confirm Delete", "Delete the selected record? Related bookings may prevent deletion."):
            return
        try:
            with get_connection() as connection:
                connection.execute(f"DELETE FROM {table} WHERE {config['pk']}=?", (record_id,))
            self.refresh_all_open_tables()
        except sqlite3.IntegrityError:
            messagebox.showerror("Cannot Delete", "This record is linked to existing bookings. Delete those bookings first.")

    def show_related(self, table, tree):
        record_id = self.selected_id(tree)
        if record_id is None:
            return
        if table == "users":
            self.open_related_window("Customer's Bookings", """
                SELECT b.booking_id,b.user_id,b.date_id,b.guests,b.total_price
                FROM bookings b WHERE b.user_id=?
            """, (record_id,), ["Booking ID", "Customer ID", "Date ID", "Guests", "Total Price"])
        elif table == "available_dates":
            self.open_related_window("Bookings for this Service", """
                SELECT b.booking_id,b.user_id,b.date_id,b.guests,b.total_price
                FROM bookings b WHERE b.date_id=?
            """, (record_id,), ["Booking ID", "Customer ID", "Date ID", "Guests", "Total Price"])
        else:
            with get_connection() as connection:
                row = connection.execute("""
                    SELECT b.user_id,u.name,u.email,u.phone,b.date_id,a.service_name,
                           a.booking_date,a.time_slot,a.price
                    FROM bookings b JOIN users u ON u.user_id=b.user_id
                    JOIN available_dates a ON a.date_id=b.date_id
                    WHERE b.booking_id=?
                """, (record_id,)).fetchone()
            if row:
                self.open_related_window("Customer for Booking", """
                    SELECT user_id,name,email,phone FROM users WHERE user_id=?
                """, (row[0],), ["Customer ID", "Name", "Email", "Phone"])
                self.open_related_window("Service for Booking", """
                    SELECT date_id,service_name,booking_date,time_slot,price
                    FROM available_dates WHERE date_id=?
                """, (row[4],), ["Date ID", "Service", "Date", "Time Slot", "Price"])

    def open_related_window(self, title, query, params, headings):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("850x350")
        win.configure(bg=BG)
        frame = tk.Frame(win, bg=BG, padx=15, pady=15)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=[f"c{i}" for i in range(len(headings))],
                            show="headings")
        for index, heading in enumerate(headings):
            column = f"c{index}"
            tree.heading(column, text=heading)
            tree.column(column, width=150, anchor="center")
        tree.pack(fill="both", expand=True)
        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        if not rows:
            tk.Label(frame, text="No related records found.", bg=BG, fg=GREY).pack(pady=8)

    def export_rows(self, table):
        config = TABLES[table]
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if not path:
            return
        try:
            frame = pd.DataFrame(self.fetch_rows(table), columns=config["columns"])
            if path.lower().endswith(".csv"):
                frame.to_csv(path, index=False)
            else:
                frame.to_excel(path, index=False)
            messagebox.showinfo("Export Complete", f"Exported {len(frame)} rows.")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    def import_rows(self, table, tree):
        config = TABLES[table]
        path = filedialog.askopenfilename(
            filetypes=[("CSV and Excel files", "*.csv *.xlsx *.xls"), ("CSV files", "*.csv"),
                       ("Excel files", "*.xlsx *.xls")]
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                frame = pd.read_csv(path, dtype=str, keep_default_na=False)
            else:
                frame = pd.read_excel(path, dtype=str).fillna("")
            expected = config["columns"]
            if list(frame.columns) != expected:
                raise ValueError("The file must contain exactly these columns in this order:\n" + ", ".join(expected))
            rows_to_insert = []
            for row_number, row in frame.iterrows():
                values = {}
                for field in config["columns"]:
                    raw = str(row[field]).strip()
                    if field == config["pk"] and raw == "":
                        values[field] = None
                    elif field in config["editable"]:
                        values[field] = self.validate_value(field, raw, config["types"][field])
                    else:
                        try:
                            values[field] = int(raw)
                        except ValueError:
                            raise ValueError(f"Row {row_number + 2}: {field} must be a whole number.")
                if table == "bookings":
                    values["total_price"] = float(values["total_price"])
                rows_to_insert.append([values[field] for field in expected])
            with get_connection() as connection:
                for row in rows_to_insert:
                    if row[0] is None:
                        connection.execute(
                            f"INSERT INTO {table} ({','.join(expected[1:])}) VALUES ({','.join('?' for _ in expected[1:])})",
                            row[1:]
                        )
                    else:
                        connection.execute(
                            f"INSERT INTO {table} ({','.join(expected)}) VALUES ({','.join('?' for _ in expected)})",
                            row
                        )
            self.refresh_all_open_tables()
            messagebox.showinfo("Import Complete", f"Imported {len(rows_to_insert)} rows.")
        except Exception as error:
            messagebox.showerror("Import Error", f"No rows were imported.\n{error}")

    def refresh_all_open_tables(self):
        for table in TABLES:
            window = self.windows.get("table_" + table)
            if window is not None and window.winfo_exists():
                for widget in window.winfo_children():
                    self.find_and_refresh_tree(widget, table)

    def find_and_refresh_tree(self, widget, table):
        if isinstance(widget, ttk.Treeview):
            self.refresh_table(table, widget)
        for child in widget.winfo_children():
            self.find_and_refresh_tree(child, table)

    def open_reports(self):
        win = self.open_window("reports", "Booking Reports", "1100x760")
        if win is None:
            return
        body = tk.Frame(win, bg=BG, padx=18, pady=16)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Booking Reports", bg=BG, fg=NAVY,
                 font=("Arial", 20, "bold")).pack(anchor="w", pady=(0, 12))
        try:
            with get_connection() as connection:
                summary = pd.read_sql_query("""
                    SELECT COUNT(*) AS total_bookings,
                           COALESCE(SUM(total_price),0) AS total_revenue,
                           COALESCE(AVG(total_price),0) AS average_booking
                    FROM bookings
                """, connection)
                popular = pd.read_sql_query("""
                    SELECT a.service_name, COUNT(b.booking_id) AS booking_count
                    FROM available_dates a LEFT JOIN bookings b ON b.date_id=a.date_id
                    GROUP BY a.date_id,a.service_name
                    ORDER BY booking_count DESC,a.service_name
                """, connection)
                highest = pd.read_sql_query("""
                    SELECT b.booking_id,u.name AS customer,a.service_name,
                           b.guests,b.total_price
                    FROM bookings b JOIN users u ON u.user_id=b.user_id
                    JOIN available_dates a ON a.date_id=b.date_id
                    ORDER BY b.total_price DESC LIMIT 10
                """, connection)
            metrics = [
                ("Total Bookings", str(int(summary.iloc[0]["total_bookings"]))),
                ("Total Revenue", f"${summary.iloc[0]['total_revenue']:.2f}"),
                ("Average Booking", f"${summary.iloc[0]['average_booking']:.2f}")
            ]
            metric_frame = tk.Frame(body, bg=BG)
            metric_frame.pack(fill="x", pady=(0, 12))
            for label, value in metrics:
                card = tk.Frame(metric_frame, bg=WHITE, bd=1, relief="solid", padx=15, pady=12)
                card.pack(side="left", expand=True, fill="x", padx=5)
                tk.Label(card, text=label, bg=WHITE, fg=GREY, font=("Arial", 10)).pack()
                tk.Label(card, text=value, bg=WHITE, fg=NAVY, font=("Arial", 18, "bold")).pack(pady=(5, 0))
            figure = Figure(figsize=(9, 3.2), dpi=100)
            axis = figure.add_subplot(111)
            if not popular.empty and popular["booking_count"].sum() > 0:
                axis.bar(popular["service_name"], popular["booking_count"])
                axis.set_ylabel("Number of bookings")
                axis.set_title("Report 1: Bookings per Service")
                axis.tick_params(axis="x", rotation=12)
            else:
                axis.text(0.5, 0.5, "No bookings available yet", ha="center", va="center")
                axis.set_title("Report 1: Bookings per Service")
            figure.tight_layout()
            canvas = FigureCanvasTkAgg(figure, master=body)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            lower = tk.Frame(body, bg=BG)
            lower.pack(fill="both", expand=True, pady=(10, 0))
            left = tk.Frame(lower, bg=WHITE, bd=1, relief="solid", padx=10, pady=8)
            left.pack(side="left", fill="both", expand=True, padx=(0, 5))
            right = tk.Frame(lower, bg=WHITE, bd=1, relief="solid", padx=10, pady=8)
            right.pack(side="left", fill="both", expand=True, padx=(5, 0))
            tk.Label(left, text="Report 2: Most Booked Services", bg=WHITE, fg=NAVY,
                     font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 6))
            popular_tree = ttk.Treeview(left, columns=("service", "count"), show="headings", height=6)
            popular_tree.heading("service", text="Service")
            popular_tree.heading("count", text="Bookings")
            popular_tree.column("service", width=190)
            popular_tree.column("count", width=90, anchor="center")
            popular_tree.pack(fill="both", expand=True)
            for _, row in popular.iterrows():
                popular_tree.insert("", "end", values=(row["service_name"], int(row["booking_count"])))
            tk.Label(right, text="Report 3: Highest-Value Bookings", bg=WHITE, fg=NAVY,
                     font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 6))
            highest_tree = ttk.Treeview(right, columns=("id", "customer", "service", "guests", "total"),
                                        show="headings", height=6)
            for column, heading, width in [
                ("id", "ID", 45), ("customer", "Customer", 110),
                ("service", "Service", 115), ("guests", "Guests", 60), ("total", "Total", 85)
            ]:
                highest_tree.heading(column, text=heading)
                highest_tree.column(column, width=width, anchor="center")
            highest_tree.pack(fill="both", expand=True)
            for _, row in highest.iterrows():
                highest_tree.insert("", "end", values=(
                    row["booking_id"], row["customer"], row["service_name"],
                    row["guests"], f"${row['total_price']:.2f}"
                ))
        except Exception as error:
            messagebox.showerror("Reports Error", str(error))


if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()
