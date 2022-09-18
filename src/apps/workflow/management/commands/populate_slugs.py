from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ...models.stage import WfWorkStageList


class Command(BaseCommand):
    help = 'Populate slugs for WfWorkStageList'

    def _slugify(self, name):
        return slugify(name, allow_unicode=True)

    def handle(self, *args, **options):
        for obj in WfWorkStageList.objects.all():
            obj.slug = slugify(getattr(obj, 'name')).replace('_', '-')
            obj.save()

            self.stdout.write(self.style.SUCCESS('Successfully populated a slug for "%s"' % obj.name))
