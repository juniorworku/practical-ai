"""Runtime studios teach before practice and retain protected, aligned feedback."""
from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from academy.models import Lesson,Enrollment

class StudentDepthTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_curriculum',verbosity=0)
        call_command('import_workshop',verbosity=0)
        cls.user=User.objects.create_user(username='runtime-studio-student')
    def test_studios_and_wrong_answer_remediation(self):
        self.client.force_authenticate(self.user)
        count=0
        for lesson in Lesson.objects.filter(program__slug__in=['ai-agent-bootcamp','ai-workshops','ai-engineering-12-week','genai-accelerator']):
            learning=lesson.resources['learning']
            studio=next((c for c in learning['chapters'] if c['id']=='runtime-studio'),None)
            if not studio:continue
            count+=1;Enrollment.objects.get_or_create(user=self.user,program=lesson.program)
            question=next(q for q in learning['quiz'] if q['id']=='runtime-studio')
            public=self.client.get(f'/api/lessons/{lesson.pk}/').data['resources']['learning']
            serialized=next(q for q in public['quiz'] if q['id']=='runtime-studio')
            self.assertNotIn('correct',serialized);self.assertNotIn('option_feedback',serialized)
            self.assertEqual(serialized['review_chapter'],'runtime-studio')
            self.assertEqual(len(studio['body'].split('## Step '))-1,4)
            answers={q['id']:q['correct'] for q in learning['quiz']}
            wrong=next(o['id'] for o in question['options'] if o['id']!=question['correct'])
            answers['runtime-studio']=wrong
            response=self.client.post(f'/api/lessons/{lesson.pk}/quiz/',{'revision':learning['revision'],'answers':answers},format='json')
            self.assertEqual(response.status_code,201)
            self.assertEqual(response.data['score'],len(answers)-1)
            self.assertIn(question['option_feedback'][wrong],str(response.data))
        self.assertEqual(count,9)
