import pandas as pd
from django.core.management.base import BaseCommand
from students.models import Student

class Command(BaseCommand):
    help = "Excel fayldan studentlarni import qiladi"

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Excel faylning manzili')

    def handle(self, *args, **kwargs):
        file_path = kwargs['excel_file']
        df = pd.read_excel(file_path)  # yoki pd.read_csv() agar CSV bo‘lsa

        count = 0
        for _, row in df.iterrows():
            student, created = Student.objects.get_or_create(
                student_id=row['student_id'],
                defaults={
                    'faculty': row['faculty'],
                    'course': row['course'],
                    'direction': row['direction'],
                    'group': row['group'],
                    'full_name': row['full_name'],
                    'telegram_id': row.get('telegram_id') if 'telegram_id' in row else None
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ta student qo‘shildi."))
