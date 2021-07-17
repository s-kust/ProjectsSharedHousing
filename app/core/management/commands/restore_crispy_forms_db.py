from django.core.management import BaseCommand
from schemas.models import DataSchemas, IntegerColumn, FullNameColumn, JobColumn, CompanyColumn, PhoneColumn

class Command(BaseCommand):
    help = "Restore the state of DB tables of the Django Crispy Forms Advanced Usage Example app."

    def handle(self, *args, **options):
        self.stdout.write()
        self.stdout.write("restore_crispy_forms_db command start")
        DataSchemas.objects.all().delete()
        schema1 = DataSchemas.objects.create(name='Schema 1')
        _ = IntegerColumn.objects.create(name='int_1_range_defaluts', schema=schema1, order=1)
        _ = IntegerColumn.objects.create(name='int_2_range_modified', schema=schema1, order=2, range_low=-14,range_high = 23)
        _ = FullNameColumn.objects.create(
                name='full_name_1_ivan_ivanoff', schema=schema1, order=3, first_name="Ivan", last_name="Ivanoff")
        _ = JobColumn.objects.create(name='job_1_janitor', schema=schema1, order=4, job_name="Janitor")
        _ = CompanyColumn.objects.create(name='company_1_MSFT', schema=schema1, order=8, company_name="MSFT")
        _ = PhoneColumn.objects.create(name='phone_1', schema=schema1, order=17, phone_number="+7911234567")
        schema2 = DataSchemas.objects.create(name='Schema 2')
        _ = IntegerColumn.objects.create(name='int_1_range_defaluts', schema=schema2, order=1)
        _ = IntegerColumn.objects.create(name='int_2_range_modified', schema=schema2, order=2, range_low=-17,range_high = 27)
        _ = FullNameColumn.objects.create(name='full_name_2_john_smith', schema=schema2, order=3,
            first_name="John", last_name="Smith")
        _ = JobColumn.objects.create(name='job_2_driver', schema=schema2, order=4, job_name="Driver")
        _ = CompanyColumn.objects.create(name='company_2_AMZN', schema=schema2, order=8, company_name="AMZN")
        _ = PhoneColumn.objects.create(name='phone2', schema=schema2, order=17, phone_number="+7911234678")
        self.stdout.write("restore_crispy_forms_db command end")
        self.stdout.write()
