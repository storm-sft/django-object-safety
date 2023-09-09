from boot_django import boot_django

boot_django()

from django.core.management import call_command

call_command('runserver')
