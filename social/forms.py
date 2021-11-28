from django import forms
from .models import Service, Event, Feedback, ServiceApplication

class ServiceForm(forms.ModelForm):
    description = forms.CharField(
        label = '',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create a service...'
        })
    )
    
    servicedate = forms.DateTimeField(
        input_formats = ['%Y-%m-%d %H:%M:%S'], 
        widget = forms.DateTimeInput(
            format='%Y-%m-%d %H:%M:%S'),
    )

    class Meta:
        model = Service
        fields = ['description', 'servicedate']

class EventForm(forms.ModelForm):
    eventname = forms.CharField(
        label = '',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create an event (name)...'
        })
    )
    
    eventdescription = forms.CharField(
        label = '',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create an event (description)...'
        })
    )
    
    eventdate = forms.DateTimeField(
        input_formats = ['%Y-%m-%d %H:%M:%S'], 
        widget = forms.DateTimeInput(
            format='%Y-%m-%d %H:%M:%S'),
    )

    eventcapacity = forms.IntegerField(
        
    )

    class Meta:
        model = Event
        fields = ['eventpicture', 'eventname', 'eventdescription', 'eventdate', 'eventlocation', 'eventcapacity']

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
