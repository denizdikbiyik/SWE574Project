from django import forms
from .models import Service, Event, Feedback, ServiceApplication

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
    )

    capacity = forms.IntegerField(
        
    )

    duration = forms.IntegerField(
        
    )

    class Meta:
        model = Service
        fields = ['picture', 'name', 'description', 'servicedate', 'location', 'capacity', 'duration']

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
    )

    eventcapacity = forms.IntegerField(
        label = 'Capacity',
    )

    eventduration = forms.IntegerField(
        label = 'Duration',
    )

    eventpicture = forms.ImageField(
        label = 'Image',
    )

    class Meta:
        model = Event
        fields = ['eventpicture', 'eventname', 'eventdescription', 'eventdate', 'eventlocation', 'eventcapacity', 'eventduration']

class FeedbackForm(forms.ModelForm):
    feedback = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={'rows': '3',
                   'placeholder': 'Give Feedback...'}
        ))

    class Meta:
        model = Feedback
        fields = ['feedback']

class ServiceApplicationForm(forms.ModelForm):    

    class Meta:
        model = ServiceApplication
        fields = []
