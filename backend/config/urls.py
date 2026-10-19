from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from academy import views
router = DefaultRouter()
router.register('programs', views.ProgramViewSet)
router.register('projects', views.ProjectViewSet, basename='project')
urlpatterns = [path('admin/', admin.site.urls), path('api/', include(router.urls)), path('api/health/', views.health), path('api/auth/register/', views.register), path('api/auth/login/', views.login), path('api/auth/logout/', views.logout), path('api/me/', views.dashboard), path('api/lessons/<int:pk>/', views.lesson_detail), path('api/lessons/<int:pk>/notes/', views.save_note), path('api/learning-kit/', views.course_download), path('api/programs/<slug:slug>/enroll/', views.enroll), path('api/lessons/<int:pk>/complete/', views.complete), path('api/terminal/', views.terminal)]
