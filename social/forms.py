from django import forms
from .models import Service, Event, Feedback, ServiceApplication

# class DefFor_DateTimeInput(forms.DateTimeInput):
#     input_type = "datetime-local"
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

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
        label = '',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create a service (name)...'
        })
    )

    description = forms.CharField(
        label = '',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create a service (description)...'
        })
    )
    
    servicedate = DateTimeLocalField()

    capacity = forms.IntegerField(
        
    )

    class Meta:
        model = Service
        fields = ['picture', 'name', 'description', 'servicedate', 'location', 'capacity']



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
    
    # eventdate = forms.DateTimeField(
    #     input_formats = ['%Y-%m-%d %H:%M:%S'], 
    #     widget = forms.DateTimeInput(
    #         format='%Y-%m-%d %H:%M:%S'),
    # )

    eventdate = DateTimeLocalField()

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
