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

def student_reasons_report(request):
    students = Student.objects.annotate(
        selected_count=Count('excellent_candidates')
    )

    # Barcha sabab kalitlarini olamiz
    all_reason_keys = [key for key, _ in ExcellenceReason.REASON_CHOICES]
    reason_dict = dict(ExcellenceReason.REASON_CHOICES)

    student_data = []

    for student in students:
        # Shu student qaysi so‘rovda tanlangan
        candidates = ExcellentCandidates.objects.filter(selected_groupmates=student)

        # Ular bilan bog‘liq sabablar
        reasons_qs = ExcellenceReason.objects.filter(candidate__in=candidates)

        # Har bir sababdan nechtaligini sanash
        reason_counter = Counter(reasons_qs.values_list('reason', flat=True))

        # Har bir sabab uchun 0 yoki haqiqiy sonni qo‘yamiz
        full_reason_stats = {
            reason_dict[key]: reason_counter.get(key, 0)
            for key in all_reason_keys
        }

        student_data.append({
            'student': student,
            'selected_count': student.selected_count,
            'reasons': full_reason_stats,
        })

    return render(request, 'report/student_reasons_report.html', {
        'student_data': student_data
    })

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
    StudentSerializer, ExcellentCandidatesSerializer, ExcellenceReasonSerializer, AtRiskCandidatesSerializer, AtRiskReasonSerializer
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
