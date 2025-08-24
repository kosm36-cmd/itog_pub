import unittest
import pandas as pd
from models import Customer, Product, Order
from analysis import analyze_data
from datetime import datetime

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        # Создаем небольшие выборки клиентов
        self.customers = [
            Customer('C1', 'Ivan Ivanov', 'ivan@mail.ru', '+79991234567', 'Москва'),
            Customer('C2', 'Petr Petrov', 'petr@mail.ru', '+79997654321', 'СПб')
        ]
        # Товары
        self.products = [
            Product('P1', 'Chocolate', 'Sweet', 100),
            Product('P2', 'Candy', 'Sweet', 50)
        ]
        # Заказы
        self.orders = [
            Order('O1', self.customers[0], [self.products[0], self.products[1]], '2023-10-01'),
            Order('O2', self.customers[1], [self.products[1]], '2023-10-02'),
        ]

    def test_analyze_data_runs_without_error(self):
        # Вызовем, чтобы убедиться что ошибок не возникает
        analyze_data(self.customers, self.products, self.orders)
        # Можно дополнительно проверить, что вызов вернул None (функция рисует графики)
        self.assertIsNone(analyze_data(self.customers, self.products, self.orders))

if __name__ == '__main__':
    unittest.main()