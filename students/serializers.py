from .models import (
    Student, ExcellentCandidates, ExcellenceReason, AtRiskCandidates, AtRiskReason, SurveyParticipation
)
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
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
    selected_groupmates = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Student.objects.all()
    )
    class Meta:
        model = AtRiskCandidates
        fields = ["id", "student", "selected_groupmates", "created_at"]

class AtRiskReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtRiskReason
        fields = ["id", "candidate", "reason"]

# serializers.py
class SurveyParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyParticipation
        fields = '__all__'

    def validate(self, attrs):
        student     = attrs["student"]
        telegram_id = attrs["telegram_id"]

        if SurveyParticipation.objects.filter(student=student).exists():
            raise serializers.ValidationError("This student has already participated.")
        if SurveyParticipation.objects.filter(telegram_id=telegram_id).exists():
            raise serializers.ValidationError("This Telegram account has already participated.")
        return attrs
