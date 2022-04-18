from django import forms
from .models import Service, Event, ServiceApplication, UserRatings, EventApplication, UserProfile, Tag, User, UserComplaints
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_date(date):
    if date < timezone.now():
        raise ValidationError("Date cannot be in the past.")

def validate_date_after(date):
    if date > timezone.now():
        raise ValidationError("Date cannot be in the future.")

class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"
 
class DateTimeLocalField(forms.DateTimeField):
    input_formats = [
        "%Y-%m-%dT%H:%M:%S", 
        "%Y-%m-%dT%H:%M:%S.%f", 
        "%Y-%m-%dT%H:%M"
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M")

class ServiceForm(forms.ModelForm):
    name = forms.CharField(
        widget = forms.Textarea(attrs={
            'rows': '1',
            'placeholder': 'Create a service (name)...'
        })
    )

    description = forms.CharField(
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create a service (description)...'
        })
    )
    
    servicedate = DateTimeLocalField(
        label = 'Date Time',
        validators=[validate_date],
    )

    capacity = forms.IntegerField(
        
    )

    duration = forms.IntegerField(
        
    )

    class Meta:
        model = Service
        fields = ['picture', 'name', 'description', 'category', 'servicedate', 'location', 'capacity', 'duration']

class EventForm(forms.ModelForm):
    eventname = forms.CharField(
        label = 'Name',
        widget = forms.Textarea(attrs={
            'rows': '1',
            'placeholder': 'Create an event (name)...'
        })
    )
    
    eventdescription = forms.CharField(
        label = 'Description',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create an event (description)...'
        })
    )

    eventdate = DateTimeLocalField(
        label = 'Date Time',
        validators=[validate_date],
    )

    eventcapacity = forms.IntegerField(
        label = 'Capacity',
    )

    eventduration = forms.IntegerField(
        label = 'Duration',
    )

    class Meta:
        model = Event
        fields = ['eventpicture', 'eventname', 'eventdescription', 'eventdate', 'eventlocation', 'eventcapacity', 'eventduration']

class RatingForm(forms.ModelForm):
    RatingList =(
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    feedback = forms.CharField(
        label = 'Feedback',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Please leave your comment here...'
        })
    )
    rating = forms.ChoiceField(
        label = 'Rating',
        choices = RatingList
    )

    class Meta:
        model = UserRatings
        fields = ['rating', 'feedback']

class ComplaintForm(forms.ModelForm):
    feedback = forms.CharField(
        label = 'Feedback',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Please leave your comment here...'
        })
    )

    class Meta:
        model = UserComplaints
        fields = ['feedback']

class ServiceApplicationForm(forms.ModelForm):    

    class Meta:
        model = ServiceApplication
        fields = ['approved']

class EventApplicationForm(forms.ModelForm):    

    class Meta:
        model = EventApplication
        fields = ['approved']

class ProfileForm(forms.ModelForm):
    name = forms.CharField(
        label = 'Name',
        widget = forms.Textarea(attrs={
            'rows': '1',
            'placeholder': 'Your name...'
        })
    )
    
    bio = forms.CharField(
        label = 'Bio',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Your bio...'
        })
    )

    birth_date = DateTimeLocalField(
        label = 'Birthdate',
        validators=[validate_date_after],
    )

    class Meta:
        model = UserProfile
        fields = ['name', 'bio', 'birth_date', 'location', 'picture']

class RequestForm(forms.ModelForm):
    tag = forms.CharField(
        widget = forms.Textarea(attrs={
            'rows': '1',
            'placeholder': 'Create a request (tag)...'
        })
    )

    class Meta:
        model = Tag
        fields = ['tag', 'toPerson']
