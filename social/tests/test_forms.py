from social.forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, RequestForm
import datetime
from django.test import TestCase
from django.utils import timezone

class EventFormTest(TestCase):
    def test_event_form_name_field_label(self):
        form = EventForm()
        self.assertTrue(form.fields['eventname'].label == 'Name')

    def test_event_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = EventForm(data={'eventdate': date})
        self.assertFalse(form.is_valid())

class ServiceFormTest(TestCase):
    def test_service_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = ServiceForm(data={'servicedate': date})
        self.assertFalse(form.is_valid())