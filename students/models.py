from django.db import models

class Student(models.Model):
    faculty = models.CharField(max_length=100)
    course = models.CharField(max_length=50)
    direction = models.CharField(max_length=100)
    group = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


# 1. Model for question 1: Who in your group might get all A's?
class ExcellentCandidates(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="excellent_nominator", verbose_name="So'rov yuborgan talaba")
    selected_groupmates = models.ManyToManyField(Student, related_name="excellent_candidates", verbose_name="A'lochi deb belgilangan guruhdoshlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "A'lochi nomzodlar so'rovi"
        verbose_name_plural = "A'lochi nomzodlar so'rovlari"

    def __str__(self):
        return f"{self.student.full_name} tomonidan a'lochi deb belgilanganlar"

# 2. Model for reasons why those students might succeed
class ExcellenceReason(models.Model):
    candidate = models.ForeignKey(ExcellentCandidates, on_delete=models.CASCADE, related_name="reasons")
    REASON_CHOICES = [
        ("responsibility", "Javobgarlik hissi kuchli"),
        ("hardwork", "Tinimsiz mehnat qiladi"),
        ("attentive", "Darslarni diqqat bilan tinglaydi"),
        ("efficient_time", "Vaqtidan samarali foydalanadi"),
        ("extra_sources", "Qo‘shimcha manbalardan bilim oladi"),
        ("good_relation", "O‘qituvchilar bilan yaxshi munosabatga ega"),
        ("active_events", "Tadbirlarda faol qatnashadi"),
    ]
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)

# 3. Model for question 3: Who might fail to pass?
class AtRiskCandidates(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="atrisk_nominator", verbose_name="So'rov yuborgan talaba")
    selected_groupmates = models.ManyToManyField(Student, related_name="atrisk_candidates", verbose_name="Xavf ostida deb belgilangan guruhdoshlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Xavf ostidagi nomzodlar so'rovi"
        verbose_name_plural = "Xavf ostidagi nomzodlar so'rovlari"

    def __str__(self):
        return f"{self.student.full_name} tomonidan xavf ostida deb belgilanganlar"

# 4. Model for reasons why those students might fail
class AtRiskReason(models.Model):
    candidate = models.ForeignKey(AtRiskCandidates, on_delete=models.CASCADE, related_name="reasons")
    REASON_CHOICES = [
        ("difficulty", "Dars materialini tushunishda qiyinchilikka duch keladi"),
        ("unprepared", "Imtihonlarga yaxshi tayyorlanmaydi"),
        ("poor_time", "Vaqtini samarali boshqara olmaydi"),
        ("motivation", "Motivatsiya yetishmaydi"),
        ("confidence", "O‘ziga bo‘lgan ishonch yetarli emas"),
        ("teacher_relation", "O‘qituvchining talabaga bo‘lgan shaxsiy munosabati ta’sir qiladi"),
        ("subjective_factors", "Tanish-bilishchilik yoki boshqa subyektiv omillar ta’sir qiladi"),
    ]
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
