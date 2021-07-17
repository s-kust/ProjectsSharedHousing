from django.test import TestCase
from model_bakery import baker

def create_test_data():
    portfolio_list = baker.make('portfoliopositionsreport.Portfolio', _quantity=1)
    row_list = baker.make('portfoliopositionsreport.PortfolioRow', portfolio=portfolio_list[0], _quantity=2)
    return portfolio_list, row_list

class ModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfolio_list, cls.rows_list = create_test_data()
        
    def test_portfolio_general_column_relation(self):
        self.assertEqual(self.portfolio_list[0].portfoliorow_set.count(), 2)
        
    def test_portfolio_rows_type(self):
        for elem in self.rows_list:
            self.assertIn(elem.row_type, ["Stocks_ETFs", "Forex"])