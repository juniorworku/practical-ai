"""Curriculum upgrades preserve student identities and distinguish instructor edits."""
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from academy.models import Program, Lesson, LessonNote, Completion, Enrollment
from academy.serializers import ProgramSerializer, LessonSerializer

class PythonReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_curriculum',verbosity=0)
    def test_scope_and_advanced_teaching_are_public(self):
        course=Program.objects.get(slug='python-for-ai')
        data=ProgramSerializer(course).data
        self.assertEqual(len(data['pedagogy']['modules']),6)
        self.assertNotIn('three synthetic policies',str(data['pedagogy']))
        self.assertEqual(sum(l.minutes for l in course.lessons.all()),67*60)
        for lesson in course.lessons.all():
            learning=LessonSerializer(lesson).data['resources']['learning']
            self.assertEqual(len(learning['quiz']),5)
            self.assertEqual(len(learning['flashcards']),5)
            self.assertIn('advanced-studio',[c['id'] for c in learning['chapters']])
            self.assertNotIn('correct',learning['quiz'][0])
        for slug in ['freelancing-masterclass']:
            course=Program.objects.get(slug=slug)
            self.assertIsNone(ProgramSerializer(course).data['pedagogy'])
            self.assertIsNone(LessonSerializer(course.lessons.first()).data['resources']['pedagogy'])
    def test_known_authored_upgrade_keeps_notes_and_completion(self):
        folder=Path(__file__).resolve().parent
        current=next(p for p in json.loads((folder/'starter_curriculum.json').read_text()) if p['slug']=='python-for-ai')
        lesson=Lesson.objects.get(program__slug='python-for-ai',order=0)
        lesson_id=lesson.pk
        user=User.objects.create_user(username='revision-preservation-fixture')
        Enrollment.objects.create(user=user,program=lesson.program)
        note=LessonNote.objects.create(user=user,lesson=lesson,text='Preserve my real reading notes')
        Completion.objects.create(user=user,lesson=lesson)
        old_text='# Earlier authored Python boundary\n\nA recognized release, not an instructor edit.'
        old_learning={'chapters':[{'id':'old','body':'An earlier authored lesson'}]}
        old_revision=hashlib.sha256(json.dumps(old_learning,sort_keys=True).encode()).hexdigest()
        old_learning['revision']=old_revision
        lesson.content=old_text;lesson.content_hash=hashlib.sha256(old_text.encode()).hexdigest()
        lesson.resources={'learning':old_learning};lesson.minutes=240;lesson.save()
        # Also preserve an actual unrecognized instructor edit in the next lesson.
        custom=Lesson.objects.get(program__slug='python-for-ai',order=1)
        custom.content='Instructor-authored exercise: preserve exactly.';custom.save(update_fields=['content'])
        with tempfile.TemporaryDirectory() as temporary:
            fixture=Path(temporary)/'academy';(fixture/'management/commands').mkdir(parents=True)
            for name in ['legacy_starter_curriculum.json','previous_practical_curriculum.json','current_practical_v3.json']:
                (fixture/name).write_text((folder/name).read_text())
            (fixture/'starter_curriculum.json').write_text(json.dumps([current]))
            history=json.loads((folder/'course_book_history.json').read_text())
            history[lesson.source_id]={'content':[lesson.content_hash],'learning':[old_revision]}
            (fixture/'course_book_history.json').write_text(json.dumps(history))
            with patch('academy.management.commands.seed_curriculum.Path',return_value=fixture/'management/commands/seed_curriculum.py'):
                call_command('seed_curriculum',verbosity=0)
        lesson.refresh_from_db();custom.refresh_from_db();note.refresh_from_db()
        self.assertEqual(lesson.pk,lesson_id)
        self.assertEqual(lesson.content,current['lessons'][0]['content'])
        self.assertEqual(lesson.resources['learning']['revision'],current['lessons'][0]['resources']['learning']['revision'])
        self.assertEqual(lesson.minutes,300)
        self.assertEqual(note.text,'Preserve my real reading notes')
        self.assertTrue(Completion.objects.filter(user=user,lesson_id=lesson_id).exists())
        self.assertEqual(custom.content,'Instructor-authored exercise: preserve exactly.')
