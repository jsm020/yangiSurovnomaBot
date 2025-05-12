from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# API for updating Student's telegram_id by student_id
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
            if full_name is not None:
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
