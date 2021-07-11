import os, shutil
import glob
from django.core.management import BaseCommand
from django.core.management import call_command 

class Command(BaseCommand):
    help = "test command"

    def handle(self, *args, **options):
        self.stdout.write()
        self.stdout.write("test command start 6")       

        folder = './staticfiles/'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        call_command('collectstatic')
        self.stdout.write("test command end")
        self.stdout.write()
