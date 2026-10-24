from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create Reader and Author roles; reconcile Author post permissions.'
    def handle(self, *args, **options):
        Group.objects.get_or_create(name='Reader')
        author, _ = Group.objects.get_or_create(name='Author')
        author.permissions.set(Permission.objects.filter(content_type__app_label='blog',
                               codename__in=['add_post', 'change_post', 'delete_post', 'view_post']))
        self.stdout.write(self.style.SUCCESS('Reader and Author roles ready.'))
