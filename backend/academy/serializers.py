from rest_framework import serializers
from .models import Program, Lesson, Project
from .pedagogy import module_contract, program_contract
class LessonSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        from copy import deepcopy
        data=super().to_representation(instance)
        data['resources']=deepcopy(data['resources'])
        data['resources']['pedagogy']=module_contract(instance.program.slug,instance.module)
        learning=data['resources'].get('learning')
        if learning:
            for question in learning['quiz']:
                question.pop('correct',None)
                question.pop('explanation',None)
                question.pop('option_feedback',None)
        return data

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'module', 'order', 'minutes', 'content', 'task', 'source_url', 'source_id', 'content_hash', 'resources']
class LessonSummarySerializer(serializers.ModelSerializer):
    learning_summary = serializers.SerializerMethodField()
    def get_learning_summary(self,instance):
        learning=instance.resources.get('learning')
        if not learning:return None
        return {'chapters':len(learning.get('chapters',[])),'concepts':len(learning['concepts']),'quiz':len(learning['quiz']),'flashcards':len(learning['flashcards']),'topics':[c['title'] for c in learning.get('chapters',[]) if c['kind']!='Code study']}
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'module', 'order', 'minutes', 'learning_summary']
class ProgramSerializer(serializers.ModelSerializer):
    progression = serializers.SerializerMethodField()
    def get_progression(self,instance):
        lessons=list(instance.lessons.all())
        if not lessons:return None
        path=lessons[0].resources.get('learning',{}).get('progression')
        if not path:return None
        return {'entry':path['entry'],'independent':True,'checkpoints':[
            {'title':l.title,'source_id':l.source_id,'requirements':len(l.resources.get('learning',{}).get('progression',{}).get('coverage',[]))}
            for l in lessons if l.resources.get('learning',{}).get('progression',{}).get('coverage')]}

    pedagogy = serializers.SerializerMethodField()
    def get_pedagogy(self,instance):
        return program_contract(instance.slug,[lesson.module for lesson in instance.lessons.all()])
    lessons = LessonSummarySerializer(many=True, read_only=True)
    class Meta:
        model = Program
        fields = ['id', 'slug', 'title', 'category', 'description', 'audience', 'outcome', 'duration', 'level', 'lessons', 'pedagogy', 'progression']
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'problem', 'blueprint', 'created_at']
        read_only_fields = ['blueprint', 'created_at']
