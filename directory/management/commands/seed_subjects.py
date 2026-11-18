from django.core.management.base import BaseCommand

from directory.models import Subject

SUBJECTS = [
    "Programming 1", "Programming 2", "Data Structures", "Algorithms", "Discrete Mathematics",
    "Database Systems", "Web Development", "Calculus", "Statistics", "Physics",
    "Technical Writing", "Networking",
]


class Command(BaseCommand):
    help = "Add the starter list of subjects (safe to run more than once)."

    def handle(self, *args, **options):
        created = sum(Subject.objects.get_or_create(name=n)[1] for n in SUBJECTS)
        self.stdout.write(self.style.SUCCESS(f"{created} new subjects added ({Subject.objects.count()} total)."))