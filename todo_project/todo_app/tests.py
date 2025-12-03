from django.test import TestCase
from .models import Task

class TaskModelTest(TestCase):
    def test_create_task(self):
        t = Task.objects.create(title="Test")
        self.assertEqual(t.title, "Test")
        self.assertFalse(t.done)
