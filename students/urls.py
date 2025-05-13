
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SurveyParticipationView,
    student_filter_view,
    groupmates_by_student_id,
    ExcellentCandidatesViewSet,
    ExcellenceReasonViewSet,
    AtRiskCandidatesViewSet,
    AtRiskReasonViewSet,
    StudentTelegramIdUpdateView,
    students_api,
    good_reasons_api,
    weak_reasons_api,
)

router = DefaultRouter()
router.register(r'excellent-candidates', ExcellentCandidatesViewSet, basename='excellent-candidates')
router.register(r'excellence-reasons', ExcellenceReasonViewSet, basename='excellence-reasons')
router.register(r'atrisk-candidates', AtRiskCandidatesViewSet, basename='atrisk-candidates')
router.register(r'atrisk-reasons', AtRiskReasonViewSet, basename='atrisk-reasons')

urlpatterns = [
    path('', student_filter_view, name='student_filter'),  # Asosiy sahifa: /api/students/
    path('list/', students_api, name='students_api'),  # Talabalar ro'yxati: /api/students/list/
    path('good_reasons/', good_reasons_api, name='good_reasons'),  # /api/students/good_reasons/
    path('weak_reasons/', weak_reasons_api, name='weak_reasons'),  # /api/students/weak_reasons/
    path("survey-participations/", SurveyParticipationView.as_view()),
    path('groupmates/<str:student_id>/', groupmates_by_student_id, name='groupmates-by-student-id'),
    path('update-telegram-id/', StudentTelegramIdUpdateView.as_view(), name='update-telegram-id'),
]
urlpatterns += router.urls
