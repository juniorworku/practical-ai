from django.contrib import admin
from .models import Program, Lesson, Enrollment, Completion, Project
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 0
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'duration']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
admin.site.register([Enrollment, Completion, Project])

from .models import LessonPractice, QuizAttempt
admin.site.register([LessonPractice,QuizAttempt])

from .models import LearningPosition, LabAttempt, ProjectSubmission, CardReview, LessonQuestion, LessonIssue, LearningPlan
admin.site.register([LearningPosition,CardReview,LearningPlan])

@admin.register(LabAttempt)
class LabAttemptAdmin(admin.ModelAdmin):
    list_display = ['user','lesson','created_at']
    readonly_fields = ['user','lesson','revision','code','results','created_at']
    def has_add_permission(self,request): return False

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user','lesson','review_status','reviewer','created_at']
    list_filter = ['review_status']
    readonly_fields = ['user','lesson','revision','artifact_url','commit','evidence','measurements','review_status','review_feedback','reviewer','reviewed_at','created_at']
    def has_add_permission(self,request): return False

@admin.register(LessonQuestion)
class LessonQuestionAdmin(admin.ModelAdmin):
    list_display = ['user','lesson','answered_by','created_at']
    readonly_fields = ['user','lesson','question','created_at','answered_by']
    def save_model(self,request,obj,form,change):
        if 'answer' in form.changed_data: obj.answered_by=request.user
        super().save_model(request,obj,form,change)
    def has_add_permission(self,request): return False

@admin.register(LessonIssue)
class LessonIssueAdmin(admin.ModelAdmin):
    list_display = ['lesson','user','resolved','created_at']
    list_filter = ['resolved']
    readonly_fields = ['user','lesson','revision','description','created_at']
    def has_add_permission(self,request): return False

from .models import LiveSession, SessionReservation
@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ['title','program','starts_at','capacity']
    list_filter = ['program']
admin.site.register(SessionReservation)
