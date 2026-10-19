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
