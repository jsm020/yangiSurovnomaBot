from django.urls import path
from .views import (
    groupmates_by_student_id,
    excellent_candidates_list,
    excellence_reasons_list,
    atrisk_candidates_list,
    atrisk_reasons_list,
)

urlpatterns = [
    path('groupmates/<str:student_id>/', groupmates_by_student_id, name='groupmates-by-student-id'),
    path('excellent-candidates/', excellent_candidates_list, name='excellent-candidates-list'),
    path('excellence-reasons/', excellence_reasons_list, name='excellence-reasons-list'),
    path('atrisk-candidates/', atrisk_candidates_list, name='atrisk-candidates-list'),
    path('atrisk-reasons/', atrisk_reasons_list, name='atrisk-reasons-list'),
]
