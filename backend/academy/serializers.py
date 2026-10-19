from rest_framework import serializers
from .models import Program, Lesson, Project
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'module', 'order', 'minutes', 'content', 'task', 'source_url', 'source_id', 'content_hash', 'resources']
class LessonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'module', 'order', 'minutes']
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
