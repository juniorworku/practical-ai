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

class LearningPosition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    chapter = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','program'], name='unique_learning_position')]

class LabAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    revision = models.CharField(max_length=64)
    code = models.TextField(max_length=20000)
    results = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at','-id']

class ProjectSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    revision = models.CharField(max_length=64)
    artifact_url = models.URLField(max_length=1000)
    commit = models.CharField(max_length=80, blank=True)
    evidence = models.TextField(max_length=12000)
    measurements = models.JSONField(default=dict)
    review_status = models.CharField(max_length=20, default='awaiting_review', choices=[('awaiting_review','Awaiting review'),('changes_requested','Changes requested'),('reviewed','Reviewed')])
    review_feedback = models.TextField(blank=True, max_length=12000)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='project_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at','-id']

class CardReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    revision = models.CharField(max_length=64)
    card = models.CharField(max_length=100)
    interval_days = models.PositiveIntegerField(default=0)
    due_at = models.DateTimeField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','lesson','revision','card'], name='unique_card_review')]

class LessonQuestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.TextField(max_length=4000)
    answer = models.TextField(blank=True, max_length=6000)
    answered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='lesson_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at','-id']

class LessonIssue(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    revision = models.CharField(max_length=64)
    description = models.TextField(max_length=4000)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class LearningPlan(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.CharField(max_length=40)
    hours_per_week = models.PositiveIntegerField(default=4)
    diagnostic = models.JSONField(default=dict)

class LiveSession(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    meeting_url = models.URLField(max_length=1000)
    capacity = models.PositiveIntegerField(default=20)
    class Meta:
        ordering = ['starts_at','id']
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at':'The session must end after it starts.'})
        if not self.capacity: raise ValidationError({'capacity':'Capacity must be at least one.'})

class SessionReservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(LiveSession, related_name='reservations', on_delete=models.CASCADE)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','session'], name='unique_session_reservation')]

class AccountSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    device = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailIdentity(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

class LessonBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','lesson'], name='unique_lesson_bookmark')]
