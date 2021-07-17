from django.test import TestCase, Client
from django.urls import reverse, resolve
from schemas.models import SchemaColumn
from model_bakery import baker

ITEMS_NUMBER = 2
COLUMN_CLASSES_COUNT = 5
subclasses = [str(subClass).split('.')[-1][:-2].lower() for subClass in SchemaColumn.__subclasses__()]

def create_test_data():
    schemas = baker.make('schemas.DataSchemas', _quantity=ITEMS_NUMBER)
    int_cols = baker.make('schemas.IntegerColumn', schema=schemas[0], _quantity=ITEMS_NUMBER)
    fullname_cols = baker.make('schemas.FullNameColumn', schema=schemas[0], _quantity=ITEMS_NUMBER)
    job_cols = baker.make('schemas.JobColumn', schema=schemas[0], _quantity=ITEMS_NUMBER)
    company_cols = baker.make('schemas.CompanyColumn', schema=schemas[0], _quantity=ITEMS_NUMBER)
    phone_cols = baker.make('schemas.PhoneColumn', schema=schemas[0], _quantity=ITEMS_NUMBER)
    return(schemas, int_cols, fullname_cols, job_cols, company_cols, phone_cols)  
    
class AllSchemasViewTests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('all_schemas')
        cls.client = Client()
        cls.response = cls.client.get(cls.url)

    def test_all_schemas_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_all_schemas_status_code_post(self):
        self.response_post = self.client.post(self.url)
        self.assertEqual(self.response_post.status_code, 405) # method not allowed
    
    def test_all_schemas_template(self):
        self.assertTemplateUsed(self.response, 'all_schemas.html')

    def test_all_schemas_contains_correct_html(self):
        self.assertContains(self.response, 'Create new schema')
    
    def test_all_schemas_does_not_contain_incorrect_html(self): 
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')
    
    def test_all_schemas_url_resolves_search_view(self):
        view = resolve('/')
        self.assertEqual(view.func.__name__, 'ProjectsListView')
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        
class DeleteSchemaViewTests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schemas, cls.int_cols, cls.fullname_cols, cls.job_cols, cls.company_cols, cls.phone_cols = create_test_data()
        cls.url = reverse('delete_schema', args=[cls.schemas[0].pk])
        cls.client = Client()
        cls.response = cls.client.post(cls.url, follow = True)
        
    def test_delete_schema_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_delete_schema_status_code_get(self):
        self.response_get = self.client.get(self.url)
        self.assertEqual(self.response_get.status_code, 405) # method not allowed
    
    def test_delete_schema_template(self):
        self.assertTemplateUsed(self.response, 'all_schemas.html')

    def test_delete_schema_contains_correct_html(self):
        self.assertContains(self.response, 'Create new schema')
    
    def test_delete_schema_does_not_contain_incorrect_html(self): 
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')
        
    def test_delete_schema_redirect(self): 
        self.assertRedirects(self.response, '/schemas/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)

    def test_delete_schema_url_resolves(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, 'delete_schema')
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()        
        
class SchemaViewTests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schemas, cls.int_cols, cls.fullname_cols, cls.job_cols, cls.company_cols, cls.phone_cols = create_test_data()
        cls.url = reverse('schema_create_update', args=[cls.schemas[0].pk])
        cls.client = Client()
        cls.response = cls.client.post(cls.url)        
    
    def test_schema_status_code(self):
        self.assertEqual(self.response.status_code, 200)
            
    def test_schema_template(self):
        self.assertTemplateUsed(self.response, 'schema_create_update.html')

    def test_schema_contains_correct_html(self):
        self.assertContains(self.response, 'Column separator')
        self.assertContains(self.response, 'String character')
        self.assertContains(self.response, 'Schema Column')
        self.assertContains(self.response, 'Column name')
        self.assertContains(self.response, 'Order')
        # self.assertContains(self.response, 'I want to add a new column')
        self.assertContains(self.response, 'New column name')
    
    def test_schema_does_not_contain_incorrect_html(self): 
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')

    def test_schema_url_resolves(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, 'SchemaView')
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()          