# Generated by Django 5.2.1 on 2025-05-13 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_remove_surveyparticipation_finished_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='telegram_user_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Telegram Username'),
        ),
    ]
