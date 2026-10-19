from django.conf import settings
from django.db import models

class Program(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=30)
    description = models.TextField()
    audience = models.TextField()
    outcome = models.TextField()
    duration = models.CharField(max_length=40)
    level = models.CharField(max_length=200, default='Beginner friendly')
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order', 'id']
    def __str__(self): return self.title

class Lesson(models.Model):
    program = models.ForeignKey(Program, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    module = models.CharField(max_length=150)
    order = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField(default=20)
    content = models.TextField()
    task = models.TextField()
    source_url = models.URLField(max_length=1000, blank=True)
    source_id = models.CharField(max_length=100, blank=True)
    content_hash = models.CharField(max_length=64, blank=True)
    resources = models.JSONField(default=dict, blank=True)
    class Meta:
        ordering = ['order', 'id']
        constraints = [models.UniqueConstraint(fields=['program', 'order'], name='unique_lesson_order')]

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'program'], name='unique_enrollment')]

class Completion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'lesson'], name='unique_completion')]

class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    problem = models.TextField(max_length=3000)
    blueprint = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

class LessonNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    text = models.TextField(max_length=10000, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'lesson'], name='unique_lesson_note')]

class LessonPractice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    revision = models.CharField(max_length=64)
    reflection_answers = models.JSONField(default=dict)
    known_cards = models.JSONField(default=list)
    task_evidence = models.TextField(max_length=12000, blank=True)
    checked_criteria = models.JSONField(default=list)
    task_status = models.CharField(max_length=20, default='draft')
    version = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','lesson','revision'], name='unique_practice_revision')]

class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    revision = models.CharField(max_length=64)
    answers = models.JSONField()
    feedback = models.JSONField()
    score = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at','-id']
