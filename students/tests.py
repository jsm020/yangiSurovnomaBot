

from django.test import TestCase, Client
from django.urls import reverse
from .models import Student, ExcellentCandidates, ExcellenceReason, AtRiskCandidates, AtRiskReason, SurveyParticipation
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

class StudentFilterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            faculty="TestFaculty",
            course="1",
            direction="TestDirection",
            group="TestGroup",
            student_id="12345",
            full_name="Test Student"
        )

    def test_student_filter_view_get(self):
        url = reverse('student_filter')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Talabalarni Baholash")

    def test_student_filter_view_post_search(self):
        url = reverse('student_filter')
        data = {
            'search': 'Test Student',
            'faculty': '',
            'course': '',
            'group': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Student")


class StudentsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = Student.objects.create(
            faculty="TestFaculty",
            course="1",
            direction="TestDirection",
            group="TestGroup",
            student_id="12345",
            full_name="Test Student"
        )

    def test_students_api_get(self):
        url = reverse('students_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertEqual(response.json()[0]['full_name'], "Test Student")

    def test_students_api_filter(self):
        url = reverse('students_api')
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['full_name'], "Test Student")


class GoodWeakReasonsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_good_reasons_api(self):
        url = reverse('good_reasons')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('responsibility', response.json())

    def test_weak_reasons_api(self):
        url = reverse('weak_reasons')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('difficulty', response.json())


class GetFilterOptionsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Student.objects.create(
            faculty="TestFaculty",
            course="1",
            direction="TestDirection",
            group="TestGroup",
            student_id="12345",
            full_name="Test Student"
        )

    def test_get_filter_options(self):
        url = reverse('filter_options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.json())
        self.assertIn('groups', response.json())
