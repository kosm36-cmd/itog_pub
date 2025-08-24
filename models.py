#  models.py

from datetime import datetime

class Customer:
    def __init__(self, cid, name, email, phone, address):
        self.cid = cid
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address


class Product:
    def __init__(self, pid, name, category, price):
        self.pid = pid
        self.name = name
        self.category = category
        self.price = price


class Order:
    def __init__(self, oid, customer, products, date_str):
        self.oid = oid
        self.customer = customer
        self.products = products
        self.date = datetime.strptime(date_str, '%Y-%m-%d')
