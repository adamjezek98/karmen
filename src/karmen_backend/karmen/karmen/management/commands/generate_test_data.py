from django.core.management.base import BaseCommand, CommandError
from logging import getLogger
from users.models import User
from karmen import ROLE_USER, ROLE_ADMIN
from groups.models import Group
from printers.models import Printer


logger = getLogger()

class Command(BaseCommand):
    help = 'Generates testing data for development purposes'

    def handle(self, *args, **options):

        logger.info('Setting up admin (if not set yet).')
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(username='admin')
            admin.set_password('admin')
            admin.save()

        logger.info('Setting up regular user.')
        user, created = User.objects.get_or_create(username='user@example.com')
        user.set_password('user')
        user.save()

        logger.info('Adding printers.')
        printer_a, created = Printer.objects.get_or_create(name=f'User\'s printer')
        printer_a.set_user(user, ROLE_ADMIN)

        printer_b = Printer.objects.create(name=f'Shared r/o printer')
        printer_b.set_user(user, ROLE_USER)

        printer_c = Printer.objects.create(name=f'Group shared printer (admin)')
        group_a = Group.objects.create(name=f'Group - user is admin')
        group_a.set_user(user, ROLE_ADMIN)
        group_a.printers.add(printer_c)

        printer_d = Printer.objects.create(name=f'Group shared printer (user)')
        group_b = Group.objects.create(name=f'Group - user is user')
        group_b.set_user(user, ROLE_USER)
        group_b.printers.add(printer_d)

        printer_e = Printer.objects.create(name=f'Foreign printer')
        group_c = Group.objects.create(name=f'Group - foreign')
        group_c.printers.add(printer_a)
        group_c.printers.add(printer_b)
        group_c.printers.add(printer_c)
        group_c.printers.add(printer_d)
        logger.info('Data was generated. Log in using "user@example.com"/"user" or "admin"/"admin"')
