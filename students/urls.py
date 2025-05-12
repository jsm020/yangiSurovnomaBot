
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    groupmates_by_student_id,
    ExcellentCandidatesViewSet,
    ExcellenceReasonViewSet,
    AtRiskCandidatesViewSet,
    AtRiskReasonViewSet,
    StudentTelegramIdUpdateView,
)

router = DefaultRouter()
router.register(r'excellent-candidates', ExcellentCandidatesViewSet, basename='excellent-candidates')
router.register(r'excellence-reasons', ExcellenceReasonViewSet, basename='excellence-reasons')
router.register(r'atrisk-candidates', AtRiskCandidatesViewSet, basename='atrisk-candidates')
router.register(r'atrisk-reasons', AtRiskReasonViewSet, basename='atrisk-reasons')

urlpatterns = [
    path('groupmates/<str:student_id>/', groupmates_by_student_id, name='groupmates-by-student-id'),
    path('update-telegram-id/', StudentTelegramIdUpdateView.as_view(), name='update-telegram-id'),
]
urlpatterns += router.urls
