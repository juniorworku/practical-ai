from rest_framework import serializers
from .models import Program, Lesson, Project
class LessonSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        from copy import deepcopy
        data=super().to_representation(instance)
        data['resources']=deepcopy(data['resources'])
        learning=data['resources'].get('learning')
        if learning:
            for question in learning['quiz']:
                question.pop('correct',None)
                question.pop('explanation',None)
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
    lessons = LessonSummarySerializer(many=True, read_only=True)
    class Meta:
        model = Program
        fields = ['id', 'slug', 'title', 'category', 'description', 'audience', 'outcome', 'duration', 'level', 'lessons']
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'problem', 'blueprint', 'created_at']
        read_only_fields = ['blueprint', 'created_at']
