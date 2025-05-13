



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Student, ExcellentCandidates, ExcellenceReason, AtRiskCandidates, AtRiskReason, SurveyParticipation
from .serializers import StudentSerializer, ExcellentCandidatesSerializer, ExcellenceReasonSerializer, AtRiskCandidatesSerializer, AtRiskReasonSerializer, SurveyParticipationSerializer
from .forms import StudentFilterForm
from django.db import models
from typing import Any, Dict



def student_filter_view(request):
    form = StudentFilterForm(request.POST or None)
    students = Student.objects.all()
    if form.is_valid():
        filters = {k: v for k, v in form.cleaned_data.items() if v}
        if 'search' in filters:
            students = students.filter(full_name__icontains=filters.pop('search').strip())
        students = students.filter(**filters)
    return render(request, 'report/index.html', {
        'form': form,
        'students': students
    })

def good_reasons_api(request):
    return JsonResponse(dict(ExcellenceReason.REASON_CHOICES))

def weak_reasons_api(request):
    return JsonResponse(dict(AtRiskReason.REASON_CHOICES))

def students_api(request):
    students = Student.objects.annotate(
        evaluated=models.Exists(
            SurveyParticipation.objects.filter(student_id=models.OuterRef('pk'))
        )
    )
    params = request.GET if request.method == 'GET' else request.POST
    filters = {k: v for k, v in params.items() if v and k in ['faculty', 'course', 'group']}
    search = params.get('search', '').strip()
    if search:
        students = students.filter(full_name__icontains=search)
    if filters:
        students = students.filter(**filters)
    # Prefetch for performance
    students = students.select_related()
    students_data = []
    for student in students:
        excellent_votes = ExcellentCandidates.objects.filter(selected_groupmates=student).count()
        atrisk_votes = AtRiskCandidates.objects.filter(selected_groupmates=student).count()
        votes = {}
        excellent_reasons = ExcellenceReason.objects.filter(candidate__selected_groupmates=student).values('reason').annotate(count=models.Count('reason'))
        for item in excellent_reasons:
            votes[item['reason']] = item['count']
        atrisk_reasons = AtRiskReason.objects.filter(candidate__selected_groupmates=student).values('reason').annotate(count=models.Count('reason'))
        for item in atrisk_reasons:
            votes[item['reason']] = item['count']
        students_data.append({
            'student_id': student.student_id,
            'full_name': student.full_name,
            'faculty': student.faculty,
            'course': student.course,
            'group': student.group,
            'evaluated': student.evaluated,
            'votes': votes,
            'excellent_votes': excellent_votes,
            'atrisk_votes': atrisk_votes,
        })
    return JsonResponse(students_data, safe=False)

def get_filter_options(request):
    faculty = request.GET.get('faculty', '')
    course = request.GET.get('course', '')
    students = Student.objects.all()
    if faculty:
        students = students.filter(faculty=faculty)
    courses = students.values_list('course', flat=True).distinct()
    if course:
        students = students.filter(course=course)
    groups = students.values_list('group', flat=True).distinct()
    return JsonResponse({
        'courses': list(courses),
        'groups': list(groups),
    })














class SurveyParticipationView(generics.ListCreateAPIView):  # List+Create
    serializer_class   = SurveyParticipationSerializer
    permission_classes = [permissions.AllowAny]
    queryset           = SurveyParticipation.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get("student")
        telegram_id = self.request.query_params.get("telegram_id")
        if student_id:
            qs = qs.filter(student=student_id)
        if telegram_id:
            qs = qs.filter(telegram_id=telegram_id)
        return qs

class StudentTelegramIdUpdateView(APIView):
    def post(self, request):
        student_id = request.data.get("student_id")
        telegram_id = request.data.get("telegram_id")
        username = request.data.get("username")
        full_name = request.data.get("full_name")
        if not student_id or not telegram_id:
            return Response({"error": "student_id va telegram_id majburiy"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(student_id=student_id)
            student.telegram_id = telegram_id
            if username is not None:
                student.username = username
            if full_name:
                student.full_name = full_name
            student.save()
            return Response(StudentSerializer(student).data)
        except Student.DoesNotExist:
            return Response({"error": "Bunday student_id topilmadi"}, status=status.HTTP_404_NOT_FOUND)

class ExcellentCandidatesViewSet(viewsets.ModelViewSet):
    queryset = ExcellentCandidates.objects.all()
    serializer_class = ExcellentCandidatesSerializer

class ExcellenceReasonViewSet(viewsets.ModelViewSet):
    queryset = ExcellenceReason.objects.all()
    serializer_class = ExcellenceReasonSerializer

class AtRiskCandidatesViewSet(viewsets.ModelViewSet):
    queryset = AtRiskCandidates.objects.all()
    serializer_class = AtRiskCandidatesSerializer

class AtRiskReasonViewSet(viewsets.ModelViewSet):
    queryset = AtRiskReason.objects.all()
    serializer_class = AtRiskReasonSerializer

@api_view(["GET"])
def groupmates_by_student_id(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        raise Http404("Student not found")
    groupmates = Student.objects.filter(group=student.group).exclude(student_id=student_id)
    serializer = StudentSerializer(groupmates, many=True)
    return Response({"groupmates": serializer.data})
