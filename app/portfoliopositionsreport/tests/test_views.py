from django.test import TestCase, Client
from django.urls import reverse, resolve
from portfoliopositionsreport.models import Portfolio, PortfolioRow
from model_bakery import baker

def createTestData():
    portfolio_list = baker.make('portfoliopositionsreport.Portfolio', _quantity=1)
    row_list = baker.make('portfoliopositionsreport.PortfolioRow', portfolio=portfolio_list[0], _quantity=1)
    return portfolio_list, row_list

class AllPortfolioRowsViewTests(TestCase):
    
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.portfolio_list, self.portfolio_row_list = createTestData()
        self.url = reverse('portfolio_root')
        self.client = Client()
        self.response = self.client.get(self.url)        

    def test_all_portfolio_rows_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_all_sportfolio_rows_status_code_post(self):
        self.response_post = self.client.post(self.url)
        self.assertEqual(self.response_post.status_code, 405) # method not allowed
    
    def test_all_portfolio_rows_template(self):
        self.assertTemplateUsed(self.response, 'portfolio_all_rows.html')

    def test_all_portfolio_rows_contains_correct_html(self):
        self.assertContains(self.response, 'Last portfolio update')
    
    def test_all_portfolio_rows_does_not_contain_incorrect_html(self): 
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.') 

    def test_all_portfolio_get_context_data(self):
        self.assertEqual(self.response.context['modified_date'], self.portfolio_list[0].modified.date())
        
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()

class PortfolioRowChartsViewTests(TestCase):
    
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.portfolio_list, self.portfolio_row_list = createTestData()
        self.url = reverse('row_charts', args=[self.portfolio_row_list[0].pk])
        self.client = Client()
        self.response = self.client.get(self.url)

    def test_portfolio_row_charts_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_portfolio_row_charts_status_code_post(self):
        self.response_post = self.client.post(self.url)
        self.assertEqual(self.response_post.status_code, 405) # method not allowed
    
    def test_portfolio_row_charts_template(self):
        self.assertTemplateUsed(self.response, 'portfolio_row_charts.html')

    def test_portfolio_row_charts_contains_correct_html(self):
        self.assertContains(self.response, 'Return to the list of all portfolio items')
    
    def test_portfolio_row_charts_does_not_contain_incorrect_html(self): 
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.') 

    def test_portfolio_row_charts_get_context_data(self):
        self.assertEqual(self.response.context['row'].pk, self.portfolio_row_list[0].pk)
        
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()