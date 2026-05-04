from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


SEQUENCE_RESET_SQL = [
    'SELECT setval(pg_get_serial_sequence(\'"accounts_user_groups"\',\'id\'), 1, false)',
    'SELECT setval(pg_get_serial_sequence(\'"accounts_user_user_permissions"\',\'id\'), 1, false)',
    'SELECT setval(pg_get_serial_sequence(\'"accounts_user"\',\'id\'), 1, false)',
    'SELECT setval(pg_get_serial_sequence(\'"tasks_task"\',\'id\'), 1, false)',
    'SELECT setval(pg_get_serial_sequence(\'"auth_permission"\',\'id\'), 1, false)',
    'SELECT setval(pg_get_serial_sequence(\'"auth_group_permissions"\',\'id\'), 1, false)',
    'SELECT setval(pg_get_serial_sequence(\'"auth_group"\',\'id\'), 1, false)',
]


class Command(BaseCommand):
    help = 'Flush DB, reset sequences to 1, and seed demo data'

    def handle(self, *args, **options):
        self.stdout.write('Flushing database...')
        call_command('flush', '--no-input')

        self.stdout.write('Resetting sequences...')
        with connection.cursor() as cursor:
            for sql in SEQUENCE_RESET_SQL:
                cursor.execute(sql)

        self.stdout.write('Seeding demo data...')
        call_command('seed_demo')

        self.stdout.write(self.style.SUCCESS('Done! DB reset and seeded with IDs starting from 1.'))
