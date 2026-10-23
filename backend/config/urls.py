from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from academy import views, practice, experience, accounts, workspace
router = DefaultRouter()
router.register('programs', views.ProgramViewSet)
router.register('projects', views.ProjectViewSet, basename='project')
urlpatterns = [path('api/lessons/<int:pk>/practice/',practice.practice_state), path('api/lessons/<int:pk>/quiz/',practice.submit_quiz), path('api/programs/<slug:slug>/download/',practice.program_download), path('admin/', admin.site.urls), path('api/', include(router.urls)), path('api/health/', views.health), path('api/auth/register/', views.register), path('api/auth/login/', views.login), path('api/auth/logout/', views.logout), path('api/me/', views.dashboard), path('api/lessons/<int:pk>/', views.lesson_detail), path('api/lessons/<int:pk>/notes/', views.save_note), path('api/learning-kit/', views.course_download), path('api/programs/<slug:slug>/enroll/', views.enroll), path('api/lessons/<int:pk>/complete/', views.complete), path('api/terminal/', views.terminal)]

urlpatterns += [
    path('api/programs/<slug:slug>/preview/',experience.preview),
    path('api/lessons/<int:pk>/position/',experience.position),
    path('api/lessons/<int:pk>/lab-attempts/',experience.lab_attempts),
    path('api/lessons/<int:pk>/submissions/',experience.submissions),
    path('api/lessons/<int:pk>/review-card/',experience.review_card),
    path('api/lessons/<int:pk>/questions/',experience.questions),
    path('api/lessons/<int:pk>/issues/',experience.report_issue),
    path('api/questions/<int:pk>/answer/',experience.answer_question),
    path('api/reviews/',experience.reviews),
    path('api/review-queue/',experience.review_queue),
    path('api/learning-plan/',experience.learning_plan),
    path('api/auth/password-reset/',experience.reset_request),
    path('api/auth/password-reset/confirm/',experience.reset_confirm),
]
urlpatterns += [
    path('api/programs/<slug:slug>/capstone-files/',experience.capstone_files),
    path('api/sessions/',experience.sessions),
    path('api/sessions/<int:pk>/reservation/',experience.reserve_session),
]

urlpatterns += [
 path('api/auth/session/',accounts.session_status),
 path('api/auth/session/login/',accounts.sign_in),
 path('api/auth/session/register/',accounts.sign_up),
 path('api/auth/session/logout/',accounts.sign_out),
 path('api/account/',accounts.account),
 path('api/account/password/',accounts.change_password),
 path('api/account/sessions/',accounts.account_sessions),
 path('api/account/sessions/<int:pk>/',accounts.account_sessions),
 path('api/search/',workspace.search),
 path('api/bookmarks/',workspace.bookmarks),
 path('api/lessons/<int:pk>/bookmark/',workspace.bookmarks),
 path('api/portfolio/',workspace.portfolio),
]
