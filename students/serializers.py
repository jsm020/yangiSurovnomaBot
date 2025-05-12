from .models import (
    Student, ExcellentCandidates, ExcellenceReason, AtRiskCandidates, AtRiskReason
)
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "student_id",
            "full_name",
            "faculty",
            "course",
            "direction",
            "group",
            "telegram_id",
        ]


class ExcellentCandidatesSerializer(serializers.ModelSerializer):
    selected_groupmates = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Student.objects.all()
    )
    class Meta:
        model = ExcellentCandidates
        fields = ["id", "student", "selected_groupmates", "created_at"]

class ExcellenceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcellenceReason
        fields = ["id", "candidate", "reason"]

class AtRiskCandidatesSerializer(serializers.ModelSerializer):
    selected_groupmates = StudentSerializer(many=True, read_only=True)
    class Meta:
        model = AtRiskCandidates
        fields = ["id", "student", "selected_groupmates", "created_at"]

class AtRiskReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtRiskReason
        fields = ["id", "candidate", "reason"]
