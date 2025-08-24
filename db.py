#  db.py

import pandas as pd
import json

def save_customers_csv(filename, customers):
    data = [{'ID': c.cid, 'Имя': c.name, 'Email': c.email, 'Телефон': c.phone, 'Адрес': c.address} for c in customers]
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def load_customers_csv(filename):
    df = pd.read_csv(filename)
    return df

def save_customers_json(filename, customers):
    data = [vars(c) for c in customers]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_customers_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_products_csv(filename, products):
    data = [{'ID': p.pid, 'Название': p.name, 'Категория': p.category, 'Цена': p.price} for p in products]
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def load_products_csv(filename):
    df = pd.read_csv(filename)
    return df

def save_products_json(filename, products):
    data = [vars(p) for p in products]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_products_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_orders_csv(filename, orders):
    data = []
    for o in orders:
        data.append({
            'OrderID': o.oid,
            'CustomerID': o.customer.cid,
            'CustomerName': o.customer.name,
            'Date': o.date.strftime('%Y-%m-%d'),
            'Products': ', '.join([p.pid for p in o.products])
        })
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def load_orders_csv(filename, customers, products):
    df = pd.read_csv(filename)
    orders = []
    for _, row in df.iterrows():
        oid = str(row['OrderID']).strip()
        customer_id = str(row['CustomerID']).strip()
        date_str = str(row['Date']).strip()
        product_ids = [pid.strip() for pid in str(row['Products']).split(',')]
        customer = next((c for c in customers if c.cid == customer_id), None)
        if customer is None:
            continue
        products_list = [p for p in products if p.pid in product_ids]
        if not products_list:
            continue
        orders.append(Order(oid, customer, products_list, date_str))
    return orders

def save_orders_json(filename, orders):
    data = []
    for o in orders:
        data.append({
            'oid': o.oid,
            'customer_id': o.customer.cid,
            'products_ids': [p.pid for p in o.products],
            'date': o.date.strftime('%Y-%m-%d')
        })
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_orders_json(filename, customers, products):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    orders = []
    for item in data:
        oid = str(item['oid']).strip()
        customer_id = str(item['customer_id']).strip()
        date_str = str(item['date']).strip()
        product_ids = [pid.strip() for pid in item['products_ids']]
        customer = next((c for c in customers if c.cid == customer_id), None)
        if customer is None:
            continue
        products_list = [p for p in products if p.pid in product_ids]
        if not products_list:
            continue
        orders.append(Order(oid, customer, products_list, date_str))
    return orders
