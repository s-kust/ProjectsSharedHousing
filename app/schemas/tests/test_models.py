import collections
from django.test import TestCase
from django.core.exceptions import ValidationError
from schemas.models import SchemaColumn, PhoneColumn
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
    
class ModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.schemas, cls.int_cols, cls.fullname_cols, cls.job_cols, cls.company_cols, cls.phone_cols = create_test_data()
        
    def test_schemas_general_column_relation(self):
        self.assertEqual(self.schemas[0].schemacolumn_set.count(), ITEMS_NUMBER * COLUMN_CLASSES_COUNT)
        
    def test_schemas_specific_column_relation(self):
        subclasses_found = []
        for column in self.schemas[0].schemacolumn_set.all():
            for subclass in subclasses:
                if hasattr(column, subclass):
                    subclasses_found.append(subclass)
                    break
        subclasses_occurrences = collections.Counter(subclasses_found)
        # print(sum(subclasses_occurrences.values()))
        # print(len(subclasses_occurrences))
        # print(subclasses_occurrences)
        for element in subclasses_occurrences:
            self.assertEqual(subclasses_occurrences[element], ITEMS_NUMBER)
        self.assertEqual(len(subclasses_occurrences), COLUMN_CLASSES_COUNT)    
       
    def test_integer_column_default_values(self):
        self.assertEqual(self.int_cols[1].range_low, -20)
        self.assertEqual(self.int_cols[1].range_high, 40)
        
    def test_phone_right(self):
        # print('Inside test_phone_right')
        phone_items = baker.make('schemas.PhoneColumn', schema=self.schemas[0], _quantity=1)
        phone_item = phone_items[0]
        # from pprint import pprint
        # pprint(vars(phone_item))
        phone_item.phone_number='+421960321654'
        # print(phone_item.phone_number)
        try:
            phone_item.full_clean()
        except ValidationError as exception_msg:
            print(exception_msg)
        else:
            phone_item.save()
        self.assertEqual(PhoneColumn.objects.filter(phone_number='+421960321654').count(), 1)
        
    def test_phone_wrong_less_than_9_digits_begin_with_one(self):
        # print('Inside test_phone_wrong less_than_9_digits')
        phone_items = baker.make('schemas.PhoneColumn', schema=self.schemas[0], _quantity=1)
        phone_item = phone_items[0]
        # from pprint import pprint
        # pprint(vars(phone_item))
        phone_item.phone_number='12345678'
        with self.assertRaises(ValidationError):
            if phone_item.full_clean():
                phone_item.save()                
        self.assertEqual(PhoneColumn.objects.filter(phone_number='12345678').count(), 0)
        
    def test_phone_wrong_more_than_15_digits_not_begin_with_one(self):
        # print('Inside test_phone_wrong more_than_15_digits_not_begin_with_one')
        phone_items = baker.make('schemas.PhoneColumn', schema=self.schemas[0], _quantity=1)
        phone_item = phone_items[0]
        # from pprint import pprint
        # pprint(vars(phone_item))
        phone_item.phone_number='01234567891234567'       
        with self.assertRaises(ValidationError):
            if phone_item.full_clean():
                phone_item.save()                
        self.assertEqual(PhoneColumn.objects.filter(phone_number='01234567891234567').count(), 0)

    def test_phone_wrong_letters(self):
        # print('Inside test_phone_wrong letters')
        phone_items = baker.make('schemas.PhoneColumn', schema=self.schemas[0], _quantity=1)
        phone_item = phone_items[0]
        # from pprint import pprint
        # pprint(vars(phone_item))
        phone_item.phone_number='fq62gf'       
        with self.assertRaises(ValidationError):
            if phone_item.full_clean():
                phone_item.save()                
        self.assertEqual(PhoneColumn.objects.filter(phone_number='fq62gf').count(), 0)
             