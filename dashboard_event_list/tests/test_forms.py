from django.test import TestCase

from dashboard_event_list.forms import PeriodPickerEvent


class TestForms(TestCase):
    def test_empty_form(self):
        form = PeriodPickerEvent()
        self.assertIn("period", form.fields)
        self.assertIn("date_old", form.fields)
        self.assertIn("date_new", form.fields)
        self.assertIn("sort", form.fields)
