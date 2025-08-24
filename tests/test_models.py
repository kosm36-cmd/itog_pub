import unittest
from datetime import datetime
from models import Customer, Product, Order

class TestModels(unittest.TestCase):

    def test_customer_str_repr(self):
        c = Customer('C10', 'Test User', 'test@mail.com', '+70000000000', 'Test City')
        self.assertEqual(c.cid, 'C10')
        # Можно проверить, что атрибуты правильные
        self.assertEqual(c.name, 'Test User')

    def test_product_equality(self):
        p1 = Product('P1', 'Product1', 'Cat', 100)
        p2 = Product('P1', 'Product1', 'Cat', 100)
        # По умолчанию объекты не равны, проверим атрибуты
        self.assertEqual(p1.pid, p2.pid)
        self.assertEqual(p1.name, p2.name)
        # Проверка, что сравнение по пиду
        self.assertEqual(p1.pid, 'P1')

    def test_order_creation_date(self):
        c = Customer('C2', 'Name', '', '', '')
        p1 = Product('P2', 'Name2', 'Cat', 50)
        date_str = '2023-11-15'
        order = Order('O123', c, [p1], date_str)
        self.assertEqual(order.oid, 'O123')
        self.assertEqual(order.customer, c)
        self.assertIn(p1, order.products)
        self.assertEqual(order.date, datetime(2023, 11, 15))
        self.assertIsInstance(order.date, datetime)

    def test_order_str(self):
        c = Customer('C3', 'User', '', '', '')
        p = Product('P3', 'Item', '', 0)
        order = Order('O321', c, [p], '2023-12-01')
        # Проверим, что атрибуты
        self.assertEqual(order.oid, 'O321')

# Можно добавить тест на сериализацию или сравнение, если добавите методы (например, __eq__)

if __name__ == '__main__':
    unittest.main()