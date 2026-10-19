import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from academy.models import Program, Lesson, Enrollment

class Command(BaseCommand):
    help = 'Seed practical v2 programs; archive recognized legacy lessons and preserve learner records.'

    @transaction.atomic
    def handle(self, *args, **options):
        folder=Path(__file__).resolve().parents[2]
        data=json.loads((folder/'starter_curriculum.json').read_text())
        legacy={p['slug']:p for p in json.loads((folder/'legacy_starter_curriculum.json').read_text())}
        created_count=0
        for row in data:
            lessons=row.pop('lessons')
            slug=row.pop('slug')
            program,created=Program.objects.get_or_create(slug=slug,defaults=row)
            original=legacy.get(slug,{})
            if not created:
                # Only replace untouched legacy metadata, retaining instructor edits.
                changed=[]
                for key,value in row.items():
                    if getattr(program,key)==original.get(key, 'Beginner friendly' if key == 'level' else None) and getattr(program,key)!=value:
                        setattr(program,key,value);changed.append(key)
                if changed: program.save(update_fields=changed)
                old_texts={l['content'] for l in original.get('lessons',[])}
                old_rows=list(program.lessons.filter(content__in=old_texts))
                if old_rows:
                    archive_defaults={key:getattr(program,key) for key in ['description','audience','outcome','duration','level']}
                    archive_defaults.update(title=program.title+' · previous introduction',category='Archive',order=900+program.order)
                    archive,_=Program.objects.get_or_create(slug=slug+'-intro-v1',defaults=archive_defaults)
                    for old in old_rows:
                        old.program=archive;old.save(update_fields=['program'])
                    for user_id in Enrollment.objects.filter(program=program).values_list('user_id',flat=True):
                        Enrollment.objects.get_or_create(user_id=user_id,program=archive)
                    self.stdout.write(f'Archived {len(old_rows)} previous introductory lessons for {slug}; notes and completion identities retained.')
            for item in lessons:
                existing=program.lessons.filter(source_id=item['source_id']).first()
                if existing:
                    continue  # Never overwrite an instructor-modified practical lesson.
                occupied=program.lessons.filter(order=item['order']).first()
                if occupied:
                    # Preserve an unrecognized/custom lesson without blocking the authored sequence.
                    occupied.order=max([1000]+list(program.lessons.values_list('order',flat=True)))+1
                    occupied.save(update_fields=['order'])
                Lesson.objects.create(program=program,**item)
                created_count+=1
        self.stdout.write(self.style.SUCCESS(f'Practical programs ready: {created_count} new sessions. Instructor edits preserved.'))
