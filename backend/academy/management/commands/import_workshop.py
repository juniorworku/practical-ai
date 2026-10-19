import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from academy.models import Program, Lesson
class Command(BaseCommand):
    help = 'Import bundled workshop without overwriting instructor edits.'
    @transaction.atomic
    def handle(self, *args, **options):
        data = json.loads((Path(__file__).resolve().parents[2] / 'content/imported_curriculum.json').read_text())
        count = 0
        for row in data:
            lessons = row.pop('lessons')
            program, _ = Program.objects.get_or_create(slug=row.pop('slug'), defaults=row)
            for lesson in lessons:
                Lesson.objects.get_or_create(program=program, order=lesson.pop('order'), defaults=lesson)
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Workshop ready: {count} readings across {len(data)} paths. Existing edits preserved.'))
