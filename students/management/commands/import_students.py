import pandas as pd
from django.core.management.base import BaseCommand
from students.models import Student

class Command(BaseCommand):
    help = "Excel fayldan studentlarni import qiladi"

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Excel faylning manzili')

    def handle(self, *args, **kwargs):
        file_path = kwargs['excel_file']
        df = pd.read_excel(file_path, header=None)  # yoki pd.read_csv() agar CSV bo‘lsa
        df.columns = ["A", "B", "C", "D", "E", "F"]  # Mos ravishda: student_id, full_name, ...

        count = 0
        for _, row in df.iterrows():
            student, created = Student.objects.get_or_create(
                student_id=row['E'],
                defaults={
                    'faculty': row['A'],
                    'course': row['B'],
                    'direction': row['C'],
                    'group': row['D'],
                    'full_name': row['F'],
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ta student qo‘shildi."))
