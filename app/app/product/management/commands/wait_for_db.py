"""
django command for wait for DB
"""
import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to wait for database."""
    def handle(self, *args, **options):
        """ EntryPoint for command"""
        self.stdout.write('Waitingg for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except(Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 seconds....3')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))