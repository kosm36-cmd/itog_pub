import unittest
from models import Customer, Product, Order
from analysis import analyze_data

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        # Создаём разные данные для тестирования
        self.customers = [
            Customer('C1', 'Ivan', 'ivan@mail.ru', '+79990000000', 'Moscow'),
            Customer('C2', 'Petr', 'petr@mail.ru', '+79991111111', 'SPb')
        ]
        self.products = [
            Product('P1', 'Choc', 'Sweet', 100),
            Product('P2', 'Candy', 'Sweet', 50)
        ]
        self.orders = [
            Order('O1', self.customers[0], [self.products[0], self.products[1]], '2023-01-01'),
            Order('O2', self.customers[1], [self.products[1]], '2023-01-02')
        ]

    def test_analyze_data_normal(self):
        # Проверяет только что вызов не вызывает ошибок
        result = analyze_data(self.customers, self.products, self.orders)
        self.assertIsNone(result)

    def test_analyze_with_empty_orders(self):
        # Передать пустой список заказов, чтобы проверить отсутствие ошибок
        result = analyze_data(self.customers, self.products, [])
        self.assertIsNone(result)

    def test_analyze_with_one_customer_one_product(self):
        cust = Customer('C3', 'Anna', 'anna@mail.ru', '+79992222222', 'Novosibirsk')
        prod = Product('P3', 'Cake', 'Sweet', 200)
        orders = [Order('O3', cust, [prod], '2023-02-01')]
        result = analyze_data([cust], [prod], orders)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()