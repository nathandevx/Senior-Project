from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Resets the DB to its default state. Ran by the Heroku Scheduler addon every day at 1AM UTC time.'

    def handle(self, *args, **options):
        call_command('delete_data')
        call_command('make_dummy_users')
        call_command('make_data')
