from django.contrib import admin

from .models import Student, ExcellentCandidates, ExcellenceReason, AtRiskCandidates, AtRiskReason

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "faculty", "course", "direction", "group")


@admin.register(ExcellentCandidates)
class ExcellentCandidatesAdmin(admin.ModelAdmin):
    list_display = ("student", "created_at")
    filter_horizontal = ("selected_groupmates",)

@admin.register(ExcellenceReason)
class ExcellenceReasonAdmin(admin.ModelAdmin):
    list_display = ("candidate", "reason")

@admin.register(AtRiskCandidates)
class AtRiskCandidatesAdmin(admin.ModelAdmin):
    list_display = ("student", "created_at")
    filter_horizontal = ("selected_groupmates",)

@admin.register(AtRiskReason)
class AtRiskReasonAdmin(admin.ModelAdmin):
    list_display = ("candidate", "reason")
