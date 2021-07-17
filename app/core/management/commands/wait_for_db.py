import time
from django.db import connection
from django.core.management import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        while True:
            try:
                connection.ensure_connection()
            except Exception as expression_msg:
                print(expression_msg)
                self.stdout.write("Connection to database cannot be established.")
                time.sleep(1)
            else:
                connection.close()
                break
        self.stdout.write(self.style.SUCCESS('Database available!'))