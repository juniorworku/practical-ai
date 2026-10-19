import json,hashlib
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
        previous={l['source_id']:l for p in json.loads((folder/'previous_practical_curriculum.json').read_text()) for l in p['lessons']}
        v3={p['slug']:p for p in json.loads((folder/'current_practical_v3.json').read_text())}
        known_lessons={l['source_id']:l for p in v3.values() for l in p['lessons']}
        book_history=json.loads((folder/'course_book_history.json').read_text())
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
                    if getattr(program,key) in [original.get(key, 'Beginner friendly' if key == 'level' else None),v3.get(slug,{}).get(key)] and getattr(program,key)!=value:
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
                    versions=[previous.get(item['source_id'],{}),known_lessons.get(item['source_id'],{})]
                    fingerprints=book_history.get(item['source_id'],{'content':[],'learning':[]})
                    recognized_book=existing.content_hash in fingerprints['content'] and hashlib.sha256(existing.content.encode()).hexdigest()==existing.content_hash
                    custom_text=not recognized_book and existing.content not in [item['content'],*[version.get('content') for version in versions]]
                    updates=[]
                    for key in ['content','task','content_hash','minutes','title','module']:
                        if (getattr(existing,key) in [version.get(key) for version in versions] or (recognized_book and key in ['content','content_hash','task','minutes'])) and getattr(existing,key)!=item[key]:
                            setattr(existing,key,item[key]);updates.append(key)
                    resources=dict(existing.resources)
                    known_learning=[version.get('resources',{}).get('learning') for version in versions]
                    current_learning=resources.get('learning',{})
                    learning_fingerprint=hashlib.sha256(json.dumps({k:v for k,v in current_learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()
                    recognized_learning=current_learning.get('revision') in fingerprints['learning'] and learning_fingerprint==current_learning.get('revision')
                    if not custom_text and (recognized_learning or resources.get('learning') in [None,*known_learning] or resources.get('learning',{}).get('revision')==item['resources']['learning']['revision']):
                        for key,value in item['resources'].items():resources[key]=value
                        if resources!=existing.resources:
                            existing.resources=resources;updates.append('resources')
                    if updates:existing.save(update_fields=updates)
                    continue  # Preserve instructor-authored text and existing progress identities.
                occupied=program.lessons.filter(order=item['order']).first()
                if occupied:
                    # Preserve an unrecognized/custom lesson without blocking the authored sequence.
                    occupied.order=max([1000]+list(program.lessons.values_list('order',flat=True)))+1
                    occupied.save(update_fields=['order'])
                Lesson.objects.create(program=program,**item)
                created_count+=1
        self.stdout.write(self.style.SUCCESS(f'Practical programs ready: {created_count} new sessions. Instructor edits preserved.'))
