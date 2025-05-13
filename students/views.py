from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# API for updating Student's telegram_id by student_id
from django.shortcuts import render
from .models import ExcellentCandidates,Student
from django.db.models import Count

from django.db.models import Count
from collections import Counter
from .models import Student, ExcellentCandidates, ExcellenceReason
from rest_framework import generics, permissions   # DRF’ning tayyor sinflari
from rest_framework import generics, permissions
from .models import SurveyParticipation
from .serializers import SurveyParticipationSerializer


# -----------------------------------------------------------------------
from django.shortcuts import render
from .forms import StudentFilterForm
from .models import Student, ExcellenceReason, AtRiskReason
from django.http import JsonResponse
from django.db import models

def student_filter_view(request):
    form = StudentFilterForm()
    students = Student.objects.all()

    if request.method == 'POST':
        form = StudentFilterForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            faculty = form.cleaned_data['faculty']
            course = form.cleaned_data['course']
            group = form.cleaned_data['group']
            students = Student.objects.all()
            if search:
                students = students.filter(full_name__icontains=search.strip())
            if faculty:
                students = students.filter(faculty=faculty)
            if course:
                students = students.filter(course=course)
            if group:
                students = students.filter(group=group)

    return render(request, 'report/index.html', {
        'form': form,
        'students': students
    })

def good_reasons_api(request):
    reasons = dict(ExcellenceReason.REASON_CHOICES)
    return JsonResponse(reasons)

def weak_reasons_api(request):
    reasons = dict(AtRiskReason.REASON_CHOICES)
    return JsonResponse(reasons)

def students_api(request):
    try:
        # Talabalarni annotatsiya qilamiz (evaluated holatini aniqlash uchun)
        students = Student.objects.annotate(
            evaluated=models.Exists(
                SurveyParticipation.objects.filter(student_id=models.OuterRef('pk'))
            )
        )
        
        # GET yoki POST so'rovlarni qabul qilish
        if request.method == 'GET':
            params = request.GET
        elif request.method == 'POST':
            params = request.POST
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        # Filtirlash parametrlari
        search = params.get('search', '').strip()
        faculty = params.get('faculty', '')
        course = params.get('course', '')
        group = params.get('group', '')

        if search:
            students = students.filter(full_name__icontains=search)
        if faculty:
            students = students.filter(faculty=faculty)
        if course:
            students = students.filter(course=course)
        if group:
            students = students.filter(group=group)

        students_data = []
        for student in students:
            # 1. A'lochi talabalar uchun ovozlarni hisoblash
            excellent_votes = ExcellentCandidates.objects.filter(
                selected_groupmates=student
            ).count()
            
            # 2. Xavf ostidagi talabalar uchun ovozlarni hisoblash
            atrisk_votes = AtRiskCandidates.objects.filter(
                selected_groupmates=student
            ).count()
            
            # 3. Sabablar bo'yicha ovozlarni yig'amiz
            votes = {}
            
            # A'lochi sabablari
            excellent_reasons = ExcellenceReason.objects.filter(
                candidate__selected_groupmates=student
            ).values('reason').annotate(count=models.Count('reason'))
            
            for item in excellent_reasons:
                votes[item['reason']] = item['count']
            
            # Xavf sabablari
            atrisk_reasons = AtRiskReason.objects.filter(
                candidate__selected_groupmates=student
            ).values('reason').annotate(count=models.Count('reason'))
            
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
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_filter_options(request):
    faculty = request.GET.get('faculty', '')
    course = request.GET.get('course', '')
    response_data = {}

    # Fakultet va kurs asosida filtrlar
    students = Student.objects.all()

    if faculty:
        students = students.filter(faculty=faculty)
    
    # Noyob kurslar
    courses = students.values('course').distinct()
    response_data['courses'] = [course['course'] for course in courses]

    # Guruhlar: agar kurs tanlangan bo‘lsa, faqat o‘sha kursga tegishli guruhlar
    if course:
        students = students.filter(course=course)
    
    groups = students.values('group').distinct()
    response_data['groups'] = [group['group'] for group in groups]

    return JsonResponse(response_data)













class SurveyParticipationView(generics.ListCreateAPIView):  # List+Create
    serializer_class   = SurveyParticipationSerializer
    permission_classes = [permissions.AllowAny]
    queryset           = SurveyParticipation.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        student_id  = self.request.query_params.get("student")      # PK
        telegram_id = self.request.query_params.get("telegram_id")  # bigint

        if student_id:
            qs = qs.filter(student=student_id)          # <‑‑ PK bo‘yicha
            # yoki: qs.filter(student_id=student_id)

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
            if username:
                student.username = username
            if full_name:
                student.full_name = full_name
            student.save()
            return Response(StudentSerializer(student).data)
        except Student.DoesNotExist:
            return Response({"error": "Bunday student_id topilmadi"}, status=status.HTTP_404_NOT_FOUND)
from .models import (
    Student, ExcellentCandidates, ExcellenceReason, AtRiskCandidates, AtRiskReason
)
from .serializers import (
    StudentSerializer, ExcellentCandidatesSerializer, ExcellenceReasonSerializer, AtRiskCandidatesSerializer, AtRiskReasonSerializer, SurveyParticipationSerializer
)
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
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
@api_view(["GET", "POST"])
def excellent_candidates_list(request):
    if request.method == "GET":
        queryset = ExcellentCandidates.objects.all()
        serializer = ExcellentCandidatesSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ExcellentCandidatesSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(ExcellentCandidatesSerializer(instance).data, status=201)
        return Response(serializer.errors, status=400)

@api_view(["GET", "POST"])
def excellence_reasons_list(request):
    if request.method == "GET":
        queryset = ExcellenceReason.objects.all()
        serializer = ExcellenceReasonSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ExcellenceReasonSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(ExcellenceReasonSerializer(instance).data, status=201)
        return Response(serializer.errors, status=400)

@api_view(["GET", "POST"])
def atrisk_candidates_list(request):
    if request.method == "GET":
        queryset = AtRiskCandidates.objects.all()
        serializer = AtRiskCandidatesSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = AtRiskCandidatesSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(AtRiskCandidatesSerializer(instance).data, status=201)
        return Response(serializer.errors, status=400)

@api_view(["GET", "POST"])
def atrisk_reasons_list(request):
    if request.method == "GET":
        queryset = AtRiskReason.objects.all()
        serializer = AtRiskReasonSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = AtRiskReasonSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(AtRiskReasonSerializer(instance).data, status=201)
        return Response(serializer.errors, status=400)

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import Http404
from .models import Student
from .serializers import StudentSerializer

@api_view(["GET"])
def groupmates_by_student_id(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        raise Http404("Student not found")
    groupmates = Student.objects.filter(group=student.group).exclude(student_id=student_id)
    serializer = StudentSerializer(groupmates, many=True)
    return Response({"groupmates": serializer.data})
