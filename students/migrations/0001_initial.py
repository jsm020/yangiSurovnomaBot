# Generated by Django 5.2.1 on 2025-05-10 07:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AtRiskCandidates",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ExcellentCandidates",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("faculty", models.CharField(max_length=100)),
                ("course", models.CharField(max_length=50)),
                ("direction", models.CharField(max_length=100)),
                ("group", models.CharField(max_length=50)),
                ("student_id", models.CharField(max_length=20, unique=True)),
                ("full_name", models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name="AtRiskReason",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            (
                                "difficulty",
                                "Dars materialini tushunishda qiyinchilikka duch keladi",
                            ),
                            ("unprepared", "Imtihonlarga yaxshi tayyorlanmaydi"),
                            ("poor_time", "Vaqtini samarali boshqara olmaydi"),
                            ("motivation", "Motivatsiya yetishmaydi"),
                            ("confidence", "O‘ziga bo‘lgan ishonch yetarli emas"),
                            (
                                "teacher_relation",
                                "O‘qituvchining talabaga bo‘lgan shaxsiy munosabati ta’sir qiladi",
                            ),
                            (
                                "subjective_factors",
                                "Tanish-bilishchilik yoki boshqa subyektiv omillar ta’sir qiladi",
                            ),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reasons",
                        to="students.atriskcandidates",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExcellenceReason",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            ("responsibility", "Javobgarlik hissi kuchli"),
                            ("hardwork", "Tinimsiz mehnat qiladi"),
                            ("attentive", "Darslarni diqqat bilan tinglaydi"),
                            ("efficient_time", "Vaqtidan samarali foydalanadi"),
                            ("extra_sources", "Qo‘shimcha manbalardan bilim oladi"),
                            (
                                "good_relation",
                                "O‘qituvchilar bilan yaxshi munosabatga ega",
                            ),
                            ("active_events", "Tadbirlarda faol qatnashadi"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reasons",
                        to="students.excellentcandidates",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="excellentcandidates",
            name="selected_groupmates",
            field=models.ManyToManyField(
                related_name="excellent_candidates", to="students.student"
            ),
        ),
        migrations.AddField(
            model_name="excellentcandidates",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="excellent_nominator",
                to="students.student",
            ),
        ),
        migrations.AddField(
            model_name="atriskcandidates",
            name="selected_groupmates",
            field=models.ManyToManyField(
                related_name="atrisk_candidates", to="students.student"
            ),
        ),
        migrations.AddField(
            model_name="atriskcandidates",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="atrisk_nominator",
                to="students.student",
            ),
        ),
    ]
