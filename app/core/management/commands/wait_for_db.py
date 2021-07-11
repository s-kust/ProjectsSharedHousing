import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand
import os

class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                # connection_parameters = {}
                # connection_parameters['']
                # conn = psycopg2.connect("dbname=suppliers user=postgres password=postgres")
                # conn.close()
            except OperationalError:
                self.stdout.write('Database unavailable, waititng 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))