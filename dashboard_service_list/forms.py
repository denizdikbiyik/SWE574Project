from django import forms


class DateInput(forms.DateInput):
    input_type = "date"


activity_choices = [("service", "Services"), ("event", "Events")]
period_choices = [("week", "Last 7 Days"), ("month", "Last 30 Days"), ("all", "All"), ("select", "Select Dates")]
sort_choices = [("createddate", "Creation Date"), ("servicedate", "Delivery Date")]


class PeriodPicker(forms.Form):
    period = forms.CharField(label="Choose a Period:", widget=forms.Select(choices=period_choices))
    date_old = forms.DateField(label="Beginning Date:", widget=DateInput, required=False)
    date_new = forms.DateField(label="Ending Date:", widget=DateInput, required=False)
    sort = forms.CharField(label="Order by:", widget=forms.Select(choices=sort_choices))
