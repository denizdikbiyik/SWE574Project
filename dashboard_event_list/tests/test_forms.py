from django.test import TestCase

from dashboard_event_list.forms import PeriodPicker


class TestForms(TestCase):
    def test_empty_form(self):
        form = PeriodPicker()
        self.assertIn("period", form.fields)
        self.assertIn("date_old", form.fields)
        self.assertIn("date_new", form.fields)
        self.assertIn("sort", form.fields)