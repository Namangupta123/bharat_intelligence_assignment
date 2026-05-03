from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

USERS = [
    dict(username='naman_user', email='namangupta0330@gmail.com', password='Demo@1234', role='USER'),
    dict(username='demo_manager', email='manager@demo.com', password='Demo@1234', role='MANAGER'),
    dict(username='demo_admin', email='admin@demo.com', password='Demo@1234', role='ADMIN'),
]

TASKS = [
    dict(title='Fix critical login page bug', description='Login returns 500 on mobile Safari — investigate and patch.'),
    dict(title='Deploy v2.0 to production', description='Run DB migrations, update env vars, and promote the Docker image.'),
]


class Command(BaseCommand):
    help = 'Seed demo users and tasks for end-to-end testing'

    def handle(self, *args, **options):
        # Clear previous demo data
        User.objects.filter(username__in=[u['username'] for u in USERS]).delete()

        created_users = {}
        for u in USERS:
            user = User.objects.create_user(**u)
            created_users[u['role']] = user
            self.stdout.write(self.style.SUCCESS(
                f"  Created {u['role']}: {u['username']} / {u['password']}  (email: {u['email']})"
            ))

        regular_user = created_users['USER']
        manager = created_users['MANAGER']

        for t in TASKS:
            task = Task.objects.create(
                title=t['title'],
                description=t['description'],
                created_by=regular_user,
                assigned_manager=manager,
            )
            self.stdout.write(self.style.SUCCESS(f"  Created task [{task.id}]: {task.title}"))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('─' * 60))
        self.stdout.write(self.style.WARNING('Ready to test. Task IDs printed above.'))
        self.stdout.write(self.style.WARNING(f'Recipient email: {regular_user.email}'))
        self.stdout.write(self.style.WARNING('─' * 60))
