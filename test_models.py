# test
import unittest
from datetime import datetime
from models import Customer, Product, Order

class TestModels(unittest.TestCase):

    def test_customer_initialization(self):
        c = Customer('C1', 'Ivan Ivanov', 'ivan@mail.ru', '+79991234567', 'Москва')
        self.assertEqual(c.cid, 'C1')
        self.assertEqual(c.name, 'Ivan Ivanov')
        self.assertEqual(c.email, 'ivan@mail.ru')
        self.assertEqual(c.phone, '+79991234567')
        self.assertEqual(c.address, 'Москва')

    def test_product_initialization(self):
        p = Product('P1', 'Chocolate', 'Sweet', 100)
        self.assertEqual(p.pid, 'P1')
        self.assertEqual(p.name, 'Chocolate')
        self.assertEqual(p.category, 'Sweet')
        self.assertEqual(p.price, 100)

    def test_order_initialization(self):
        c = Customer('C1', 'Ivan Ivanov', 'ivan@mail.ru', '+79991234567', 'Москва')
        p1 = Product('P1', 'Chocolate', 'Sweet', 100)
        p2 = Product('P2', 'Candy', 'Sweet', 50)
        order_date_str = '2023-10-01'
        o = Order('O1', c, [p1, p2], order_date_str)
        self.assertEqual(o.oid, 'O1')
        self.assertEqual(o.customer, c)
        self.assertEqual(o.products, [p1, p2])
        self.assertEqual(o.date, datetime(2023, 10, 1))
        # Проверка типа date
        self.assertIsInstance(o.date, datetime)

if __name__ == '__main__':
    unittest.main()
