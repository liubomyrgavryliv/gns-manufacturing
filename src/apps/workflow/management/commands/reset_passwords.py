from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from ...models.stage import WfWorkStageList


class Command(BaseCommand):
    help = 'Reset all passwords to "password". This is for development only.'


    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write('This command is only available in DEBUG mode.')
            return
        for user in User.objects.all():
            user.set_password('password')
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully reset password for "%s"' % user.username))
