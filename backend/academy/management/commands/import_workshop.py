import hashlib,json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from academy.models import Program,Lesson

def fingerprint(learning):
    return hashlib.sha256(json.dumps({k:v for k,v in learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()

class Command(BaseCommand):
    help='Import source readings and reviewed Accelerator/Tutor books, preserving instructor edits and learner identities.'
    @transaction.atomic
    def handle(self,*args,**options):
        folder=Path(__file__).resolve().parents[2]/'content'
        source=json.loads((folder/'imported_curriculum.json').read_text())
        reviewed={p['slug']:p for p in json.loads((folder/'reviewed_workshop.json').read_text())}
        history=json.loads((folder/'imported_teaching_history.json').read_text())
        created=updated=preserved=0
        for original_program in source:
            slug=original_program['slug'];target=reviewed.get(slug,original_program)
            program,new=Program.objects.get_or_create(slug=slug,defaults={k:v for k,v in target.items() if k not in {'slug','lessons'}})
            if not new:
                fields=[]
                for key,value in target.items():
                    if key not in {'slug','lessons'} and getattr(program,key)==original_program[key] and value!=getattr(program,key):
                        setattr(program,key,value);fields.append(key)
                if fields:program.save(update_fields=fields)
            originals={l['source_id']:l for l in original_program['lessons']}
            if slug in reviewed:
                desired={r['source_id']:r['order'] for r in target['lessons']}
                existing=list(program.lessons.all())
                original_order={k:v['order'] for k,v in originals.items()}
                actual={r.source_id:r.order for r in existing}
                # The complete authored sequence is either the old release or
                # the new release. Preserve any unrecognized instructor order.
                if actual==original_order or actual==desired:
                    base=max([1000]+[r.order for r in existing])+len(existing)+1
                    for offset,lesson in enumerate(existing):
                        lesson.order=base+offset;lesson.save(update_fields=['order'])
                    for lesson in existing:
                        lesson.order=desired[lesson.source_id];lesson.save(update_fields=['order'])
            for item in target['lessons']:
                lesson=program.lessons.filter(source_id=item['source_id']).first()
                if lesson is None:
                    occupied=program.lessons.filter(order=item['order']).first()
                    if occupied:
                        occupied.order=max([1000]+list(program.lessons.values_list('order',flat=True)))+1
                        occupied.save(update_fields=['order'])
                    Lesson.objects.create(program=program,**item);created+=1;continue
                if slug not in reviewed:continue
                old=originals[item['source_id']];known=history[item['source_id']]
                actual_hash=hashlib.sha256(lesson.content.encode()).hexdigest();current=lesson.resources.get('learning')
                recognized_text=lesson.content==old['content'] or actual_hash in known['content']
                recognized_learning=current is None or (fingerprint(current)==current.get('revision') and current.get('revision') in known['learning'])
                recognized_task=lesson.task in [old['task'],item['task'],*known.get('fields',{}).get('task',[])]
                if not recognized_text or not recognized_learning or not recognized_task:preserved+=1;continue
                changes=[]
                for key in ['content','content_hash','task','title','module','minutes']:
                    expected_values=[old[key],item[key],*known.get('fields',{}).get(key,[])]
                    if (key in {'content','content_hash'} or getattr(lesson,key) in expected_values) and getattr(lesson,key)!=item[key]:
                        setattr(lesson,key,item[key]);changes.append(key)
                resources={**lesson.resources,'learning':item['resources']['learning'],'reviewed_source_hash':old['content_hash']}
                if resources!=lesson.resources:lesson.resources=resources;changes.append('resources')
                if changes:lesson.save(update_fields=changes);updated+=1
        self.stdout.write(self.style.SUCCESS(f'Workshop ready: {created} new; {updated} reviewed books upgraded; {preserved} instructor edits preserved.'))
