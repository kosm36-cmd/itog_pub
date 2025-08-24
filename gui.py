#  gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

from models import Customer, Product, Order
from db import (
    save_customers_csv, load_customers_csv,
    save_customers_json, load_customers_json,
    save_products_csv, load_products_csv,
    save_products_json, load_products_json,
    save_orders_csv, load_orders_csv,
    save_orders_json, load_orders_json
)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет + Аналитика")
        self.customers = []
        self.products = []
        self.orders = []

        self.create_tabs()
        self.load_sample_data()

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)

        self.tab_cust = ttk.Frame(self.notebook)
        self.tab_prods = ttk.Frame(self.notebook)
        self.tab_orders = ttk.Frame(self.notebook)
        self.tab_analysis = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_cust, text='Клиенты')
        self.notebook.add(self.tab_prods, text='Товары')
        self.notebook.add(self.tab_orders, text='Заказы')
        self.notebook.add(self.tab_analysis, text='Аналитика')

        self.notebook.pack(fill='both', expand=True)

        self.setup_customers_tab()
        self.setup_products_tab()
        self.setup_orders_tab()
        self.setup_analysis_tab()

        # Добавляем методы экспорта/импорта для кнопок
        # Сделано т.к. button'ы вызывают методы,
        # которых вначале не было, добавим их ниже...

    # ===========================================
    # ----------------- Клиенты ------------------
    # ===========================================
    def setup_customers_tab(self):
        frame = self.tab_cust
        menu_frame = ttk.Frame(frame)
        menu_frame.pack(pady=5, fill='x')
        ttk.Button(menu_frame, text='Экспорт CSV', command=self.export_customers_csv).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Импорт CSV', command=self.import_customers_csv).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Экспорт JSON', command=self.export_customers_json).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Импорт JSON', command=self.import_customers_json).pack(side='left', padx=2)

        filter_frame = ttk.Frame(frame)
        filter_frame.pack(pady=5, fill='x')
        ttk.Label(filter_frame, text='Фильтр по имени:').pack(side='left')
        self.cf_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.cf_var, width=20).pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Применить', command=self.filter_customers).pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Сброс', command=self.refresh_customers).pack(side='left', padx=2)

        self.tree_cust = ttk.Treeview(frame, columns=('ID', 'Name', 'Email', 'Phone', 'Address'), show='headings')
        for col in ('ID', 'Name', 'Email', 'Phone', 'Address'):
            self.tree_cust.heading(col, text=col, command=lambda c=col: self.sort_tree(self.tree_cust, c))
            self.tree_cust.column(col, width=130)
        self.tree_cust.pack(fill='both', expand=True)

        ttk.Button(frame, text='Добавить клиента', command=self.open_add_customer_window).pack(pady=5)

    def filter_customers(self):
        key = self.cf_var.get().lower()
        filtered = [c for c in self.customers if key in c.name.lower()]
        self.display_customers(filtered)

    def display_customers(self, list_cust):
        for i in self.tree_cust.get_children():
            self.tree_cust.delete(i)
        for c in list_cust:
            self.tree_cust.insert('', 'end', values=(c.cid, c.name, c.email, c.phone, c.address))

    def refresh_customers(self):
        self.display_customers(self.customers)

    def load_sample_customers(self):
        self.customers = [
            Customer('C1', 'Иван Иванов', 'ivan@mail.ru', '+79991234567', 'Москва'),
            Customer('C2', 'Петр Петров', 'petr@mail.ru', '+79997654321', 'СПб'),
            Customer('C3', 'Аня Смирнова', 'anna@mail.ru', '+79998887766', 'Новосибирск'),
            Customer('C4', 'Михаил К.', 'michael@mail.ru', '+79995554433', 'Казань'),
            Customer('C5', 'Настя Иванова', 'nasti@mail.ru', '+79991112233', 'Ростов')
        ]
        self.refresh_customers()

    def open_add_customer_window(self):
        w = tk.Toplevel()
        w.title('Добавить клиента')
        entries = {}
        for lbl in ['ID', 'Имя', 'Email', 'Телефон', 'Адрес']:
            ttk.Label(w, text=lbl).pack()
            e = ttk.Entry(w, width=30)
            e.pack()
            entries[lbl] = e

        def validate_email(email):
            return '@' in email and '.' in email

        def validate_phone(phone):
            return phone.startswith('+') and phone[1:].isdigit()

        def validate_non_empty(val):
            return bool(val.strip())

        def validate_entry(entry, v_type='text'):
            v = entry.get()
            if v_type == 'non_empty':
                return validate_non_empty(v)
            elif v_type == 'email':
                return validate_email(v)
            elif v_type == 'phone':
                return validate_phone(v)
            else:
                return True

        for lbl, en in entries.items():
            v_type = {'ID':'non_empty','Имя':'non_empty','Email':'email','Телефон':'phone','Адрес':'non_empty'}[lbl]
            def on_key(e, en=en, vtype=v_type):
                valid = validate_entry(en, vtype)
                en.config(foreground='black' if valid else 'red')
            en.bind('<KeyRelease>', on_key)

        def save():
            valid = True
            for lbl, e in entries.items():
                v_type = {'ID':'non_empty','Имя':'non_empty','Email':'email','Телефон':'phone','Адрес':'non_empty'}[lbl]
                if not validate_entry(e, v_type):
                    valid=False
            if not valid:
                messagebox.showwarning("Ошибка", "Проверьте введённые данные")
                return
            cid = entries['ID'].get().strip()
            name = entries['Имя'].get().strip()
            email = entries['Email'].get().strip()
            phone = entries['Телефон'].get().strip()
            addr = entries['Адрес'].get().strip()
            if any(c.cid == cid for c in self.customers):
                messagebox.showerror('Ошибка', 'ID уже есть')
                return
            self.customers.append(Customer(cid, name, email, phone, addr))
            self.refresh_customers()
            w.destroy()

        ttk.Button(w, text='Сохранить', command=save).pack(pady=10)

    # ===========================================
    # ---------------- Товары --------------------
    # ===========================================
    def setup_products_tab(self):
        frame = self.tab_prods
        menu_frame = ttk.Frame(frame)
        menu_frame.pack(pady=5, fill='x')
        ttk.Button(menu_frame, text='Экспорт CSV', command=self.export_products_csv).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Импорт CSV', command=self.import_products_csv).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Экспорт JSON', command=self.export_products_json).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Импорт JSON', command=self.import_products_json).pack(side='left', padx=2)

        self.tree_p = ttk.Treeview(frame, columns=('ID', 'Name', 'Category', 'Price'), show='headings')
        for col in ('ID', 'Name', 'Category', 'Price'):
            self.tree_p.heading(col, text=col, command=lambda c=col: self.sort_tree(self.tree_p, c))
            self.tree_p.column(col, width=130)
        self.tree_p.pack(fill='both', expand=True)

        self.p_menu = tk.Menu(self.tab_prods, tearoff=0)
        self.p_menu.add_command(label="Редактировать", command=self.edit_product)
        self.p_menu.add_command(label="Удалить", command=self.delete_product)
        self.p_menu.add_separator()
        self.p_menu.add_command(label="Добавить товар", command=self.open_add_product_window)

        self.tree_p.bind("<Button-3>", self.show_product_context_menu)
        ttk.Button(frame, text='Добавить товар', command=self.open_add_product_window).pack(pady=5)

    def load_sample_products(self):
        self.products = [
            Product('P1', 'Шоколад', 'Конфеты', 80),
            Product('P2', 'Жвачка', 'Жвачки', 20),
            Product('P3', 'Леденцы', 'Конфеты', 50),
            Product('P4', 'Мармелад', 'Конфеты', 70),
            Product('P5', 'Печенье', 'Снеки', 90),
            Product('P6', 'Кофе', 'Напитки', 150),
            Product('P7', 'Чай', 'Напитки', 120),
            Product('P8', 'Газировка', 'Напитки', 60),
            Product('P9', 'Сухарики', 'Снеки', 80),
            Product('P10', 'Миндаль', 'Орехи', 200),
        ]
        self.refresh_products()

    def refresh_products(self):
        for i in self.tree_p.get_children():
            self.tree_p.delete(i)
        for p in self.products:
            self.tree_p.insert('', 'end', values=(p.pid, p.name, p.category, p.price))

    def open_add_product_window(self):
        w = tk.Toplevel()
        w.title('Добавить товар')
        entries = {}
        for lbl in ['ID', 'Название', 'Категория', 'Цена']:
            ttk.Label(w, text=lbl).pack()
            e = ttk.Entry(w, width=30)
            e.pack()
            entries[lbl] = e

        def validate_price(val):
            try:
                float(val)
                return True
            except:
                return False

        def validate_non_empty(val):
            return bool(val.strip())

        def validate_entry(entry, v_type='text'):
            v = entry.get()
            if v_type == 'non_empty':
                return validate_non_empty(v)
            elif v_type == 'price':
                return validate_price(v)
            else:
                return True

        for lbl, en in entries.items():
            v_type = {'ID':'non_empty','Название':'non_empty','Категория':'non_empty','Цена':'price'}[lbl]
            def on_key(e, en=en, vtype=v_type):
                valid = validate_entry(en, vtype)
                en.config(foreground='black' if valid else 'red')
            en.bind('<KeyRelease>', on_key)

        def save():
            valid = True
            for lbl, e in entries.items():
                v_type = {'ID':'non_empty','Название':'non_empty','Категория':'non_empty','Цена':'price'}[lbl]
                if not validate_entry(e, v_type):
                    valid=False
            if not valid:
                messagebox.showwarning("Ошибка", "Проверьте правильность данных")
                return
            try:
                price = float(entries['Цена'].get().strip())
            except:
                messagebox.showerror('Ошибка', 'Некорректная цена')
                return
            if any(p.pid == entries['ID'].get().strip() for p in self.products):
                messagebox.showerror('Ошибка', 'ID уже есть')
                return
            self.products.append(Product(
                entries['ID'].get().strip(),
                entries['Название'].get().strip(),
                entries['Категория'].get().strip(),
                price
            ))
            self.refresh_products()
            w.destroy()

        ttk.Button(w, text='Сохранить', command=save).pack(pady=10)

    def show_product_context_menu(self, event):
        row_id = self.tree_p.identify_row(event.y)
        if row_id:
            self.tree_p.selection_set(row_id)
            self.p_menu.tk_popup(event.x_root, event.y_root)

    def delete_product(self):
        selected = self.tree_p.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self.tree_p.item(item_id)['values']
        pid = str(values[0])
        if messagebox.askyesno("Удаление", f"Удалить товар '{values[1]}'?"):
            self.products = [p for p in self.products if p.pid != pid]
            self.refresh_products()

    def edit_product(self):
        selected = self.tree_p.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self.tree_p.item(item_id)['values']
        pid = str(values[0])
        product = next((p for p in self.products if p.pid == pid), None)
        if not product:
            return
        w = tk.Toplevel()
        w.title('Редактировать товар')
        entries = {}
        lbls = ['ID', 'Название', 'Категория', 'Цена']
        vals = [product.pid, product.name, product.category, str(product.price)]
        for lbl, val in zip(lbls, vals):
            ttk.Label(w, text=lbl).pack()
            e = ttk.Entry(w, width=30)
            e.insert(0, val)
            e.pack()
            entries[lbl] = e

        def validate_price(val):
            try:
                float(val)
                return True
            except:
                return False

        def validate_non_empty(val):
            return bool(val.strip())

        def validate_entry(entry, v_type='text'):
            v = entry.get()
            if v_type == 'non_empty':
                return validate_non_empty(v)
            elif v_type == 'price':
                return validate_price(v)
            else:
                return True

        for lbl, en in entries.items():
            v_type = {'ID':'non_empty','Название':'non_empty','Категория':'non_empty','Цена':'price'}[lbl]
            def on_key(e, en=en, vtype=v_type):
                valid = validate_entry(en, vtype)
                en.config(foreground='black' if valid else 'red')
            en.bind('<KeyRelease>', on_key)

        def save():
            valid = True
            for lbl, e in entries.items():
                v_type = {'ID':'non_empty','Название':'non_empty','Категория':'non_empty','Цена':'price'}[lbl]
                if not validate_entry(e, v_type):
                    valid=False
            if not valid:
                messagebox.showwarning("Ошибка", "Проверьте правильность данных")
                return
            try:
                new_price = float(entries['Цена'].get().strip())
            except:
                messagebox.showerror('Ошибка', 'Некорректная цена')
                return
            new_pid = entries['ID'].get().strip()
            if new_pid != pid and any(p.pid == new_pid for p in self.products):
                messagebox.showerror('Ошибка', 'ID уже есть')
                return
            product.pid = new_pid
            product.name = entries['Название'].get().strip()
            product.category = entries['Категория'].get().strip()
            product.price = new_price
            self.refresh_products()
            w.destroy()

        ttk.Button(w, text='Сохранить', command=save).pack(pady=10)

    # ===========================================
    # ---------------- Заказы -------------------
    # ===========================================
    def setup_orders_tab(self):
        frame = self.tab_orders
        # фильтр
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(pady=5, fill='x')
        ttk.Label(filter_frame, text='Фильтр по дате (ГГГГ-ММ-ДД):').pack(side='left')
        self.order_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.order_date_var, width=15).pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Фильтр по клиенту:').pack(side='left', padx=10)
        self.order_client_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.order_client_var, width=20).pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Фильтр по товару:').pack(side='left', padx=10)
        self.order_product_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.order_product_var, width=20).pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Применить', command=self.filter_orders).pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Сброс', command=self.refresh_orders).pack(side='left', padx=2)

        # таблица заказов
        self.tree_o = ttk.Treeview(frame, columns=('OrderID', 'Customer', 'Date', 'Products'), show='headings')
        for col in ('OrderID', 'Customer', 'Date', 'Products'):
            self.tree_o.heading(col, text=col, command=lambda c=col: self.sort_tree(self.tree_o, c))
            self.tree_o.column(col, width=150)
        self.tree_o.pack(fill='both', expand=True)

        ttk.Button(frame, text='Добавить заказ', command=self.open_add_order_window).pack(pady=5)

        # Экспорт/импорт
        menu_frame = ttk.Frame(frame)
        menu_frame.pack(pady=5, fill='x')
        ttk.Button(menu_frame, text='Экспорт CSV', command=self.export_orders_csv).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Импорт CSV', command=self.import_orders_csv).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Экспорт JSON', command=self.export_orders_json).pack(side='left', padx=2)
        ttk.Button(menu_frame, text='Импорт JSON', command=self.import_orders_json).pack(side='left', padx=2)

        self.load_sample_orders()

    def load_sample_orders(self):
        if not self.customers or not self.products:
            return
        c_list = self.customers
        p_list = self.products
        dates = [f'2023-09-{d:02d}' for d in range(1, 21)]
        for i in range(1, 21):
            c = c_list[i % len(c_list)]
            sel_products = [p_list[(i + j) % len(p_list)] for j in range(1, (i % 3) + 2)]
            self.orders.append(Order(f"O{i:02d}", c, sel_products, dates[i - 1]))
        self.refresh_orders()

    def refresh_orders(self):
        self.display_orders(self.orders)

    def display_orders(self, list_orders):
        for i in self.tree_o.get_children():
            self.tree_o.delete(i)
        for o in list_orders:
            pname = ', '.join(p.name for p in o.products)
            self.tree_o.insert('', 'end', values=(o.oid, o.customer.name, o.date.strftime('%Y-%m-%d'), pname))

    def filter_orders(self):
        date_f = self.order_date_var.get().strip()
        client_f = self.order_client_var.get().lower()
        product_f = self.order_product_var.get().lower()
        filtered = []
        for o in self.orders:
            if date_f and date_f not in o.date.strftime('%Y-%m-%d'):
                continue
            if client_f and client_f not in o.customer.name.lower():
                continue
            if product_f:
                if not any(product_f in p.name.lower() for p in o.products):
                    continue
            filtered.append(o)
        self.display_orders(filtered)

    def open_add_order_window(self):
        w = tk.Toplevel()
        w.title('Добавить заказ')
        ttk.Label(w, text='Выберите клиента:').pack()
        c_var = tk.StringVar()
        c_cb = ttk.Combobox(w, textvariable=c_var, state='readonly', width=30)
        c_cb['values'] = [f"{c.cid} - {c.name}" for c in self.customers]
        if c_cb['values']:
            c_cb.current(0)
        c_cb.pack()

        ttk.Label(w, text='Выберите товары:').pack(pady=(10, 0))
        listbox = tk.Listbox(w, selectmode='multiple', height=10)
        for p in self.products:
            listbox.insert('end', f"{p.pid} - {p.name}")
        listbox.pack()

        ttk.Label(w, text='Дата (ГГГГ-ММ-ДД):').pack(pady=(10, 0))
        date_entry = tk.Entry(w)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack()

        def save():
            sel_idx = listbox.curselection()
            if not sel_idx:
                messagebox.showwarning('Ошибка', 'Выберите товары')
                return
            c_idx = c_cb.current()
            if c_idx == -1:
                messagebox.showwarning('Ошибка', 'Выберите клиента')
                return
            c = self.customers[c_idx]
            sel_products = [self.products[i] for i in sel_idx]
            date_str = date_entry.get().strip()
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except:
                messagebox.showerror('Ошибка', 'Некорректная дата')
                return
            self.orders.append(Order(f"O{len(self.orders)+1:02d}", c, sel_products, date_str))
            self.refresh_orders()
            w.destroy()

        ttk.Button(w, text='Создать', command=save).pack(pady=10)

    # ===========================================
    # -------------- Аналитика -------------------
    # ===========================================
    def setup_analysis_tab(self):
        lbl = tk.Label(self.tab_analysis, text="Аналитика в разработке", font=('Arial', 14))
        lbl.pack(pady=10)
        ttk.Button(self.tab_analysis, text='Запуск анализа', command=self.run_analysis).pack(pady=10)

    def run_analysis(self):
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        import networkx as nx

        if not self.orders:
            messagebox.showinfo("Аналитика", "Нет данных для анализа")
            return

        from analysis import analyze_data
        analyze_data(self.customers, self.products, self.orders)

    # ===================== Методы экспорта/импорта ---------------------
    # Эти методы добавлены для работы с кнопками
    
    # ---------------- Клиенты ------------------
    def export_customers_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                save_customers_csv(filename, self.customers)
                messagebox.showinfo("Экспорт", "Клиенты успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def import_customers_csv(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.customers = load_customers_csv(filename)
                self.refresh_customers()
                messagebox.showinfo("Импорт", "Клиенты успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    def export_customers_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            try:
                save_customers_json(filename, self.customers)
                messagebox.showinfo("Экспорт", "Клиенты успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def import_customers_json(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.customers = load_customers_json(filename)
                self.refresh_customers()
                messagebox.showinfo("Импорт", "Клиенты успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    # ---------------- Товары ------------------
    def export_products_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV файлы", "*.csv")])
        if filename:
            try:
                save_products_csv(filename, self.products)
                messagebox.showinfo("Экспорт", "Товары успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def import_products_csv(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.products = load_products_csv(filename)
                self.refresh_products()
                messagebox.showinfo("Импорт", "Товары успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    def export_products_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            try:
                save_products_json(filename, self.products)
                messagebox.showinfo("Экспорт", "Товары успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def import_products_json(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.products = load_products_json(filename)
                self.refresh_products()
                messagebox.showinfo("Импорт", "Товары успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    # ---------------- Заказы ------------------
    def export_orders_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV файлы", "*.csv")])
        if filename:
            try:
                save_orders_csv(filename, self.orders)
                messagebox.showinfo("Экспорт", "Заказы успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def import_orders_csv(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.orders = load_orders_csv(filename, self.customers, self.products)
                self.refresh_orders()
                messagebox.showinfo("Импорт", "Заказы успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    def export_orders_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            try:
                save_orders_json(filename, self.orders)
                messagebox.showinfo("Экспорт", "Заказы успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def import_orders_json(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.orders = load_orders_json(filename, self.customers, self.products)
                self.refresh_orders()
                messagebox.showinfo("Импорт", "Заказы успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    # ===========================
    # --- пример загрузки данных ---
    def load_sample_data(self):
        self.load_sample_customers()
        self.load_sample_products()
        if self.customers and self.products:
            self.load_sample_orders()
