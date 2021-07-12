import time
from django.db import connection
from django.db.utils import OperationalError
from django.core.management import BaseCommand
import os

class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        while True:
            try:
                connection.ensure_connection()
            except Exception as e:
                print(e)
                self.stdout.write("Connection to database cannot be established.")
                time.sleep(1)
            else:
                connection.close()
                break
        self.stdout.write(self.style.SUCCESS('Database available!'))