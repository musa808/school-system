from django.core.management.base import BaseCommand
from school.models import User

class Command(BaseCommand):
    help = 'Create superuser if none exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='Admin1234!'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            u = User.objects.get(username='admin')
            u.set_password('Admin1234!')
            u.is_superuser = True
            u.is_staff = True
            u.is_active = True
            u.save()
            self.stdout.write(self.style.SUCCESS('Superuser password reset successfully'))