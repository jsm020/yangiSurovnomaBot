from django import forms
from .models import Student

class StudentFilterForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label="Qidiruv", widget=forms.TextInput(attrs={'placeholder': '🔍 Talaba ismini yozing...'}))
    faculty = forms.ChoiceField(choices=[], label="Fakultet", required=False)
    course = forms.ChoiceField(choices=[], label="Kurs", required=False)
    group = forms.ChoiceField(choices=[], label="Guruh", required=False)

    def __init__(self, *args, **kwargs):
        super(StudentFilterForm, self).__init__(*args, **kwargs)
        # Fakultetlarni modeldan olish
        faculties = Student.objects.values_list('faculty', flat=True).distinct()
        self.fields['faculty'].choices = [('', '🏫 Fakultet')] + [(f, f) for f in faculties]

        # Kurslarni modeldan olish
        courses = Student.objects.values_list('course', flat=True).distinct()
        self.fields['course'].choices = [('', '📘 Kurs')] + [(c, c) for c in courses]

        # Guruhlarni modeldan olish
        groups = Student.objects.values_list('group', flat=True).distinct()
        self.fields['group'].choices = [('', '👥 Guruh')] + [(g, g) for g in groups]