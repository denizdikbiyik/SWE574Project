from django import forms


class DateInput(forms.DateInput):
    input_type = "date"


period_choices = [("week", "Last 7 Days"), ("month", "Last 30 Days"), ("all", "All"), ("select", "Select Dates")]


class PeriodPicker(forms.Form):
    period = forms.CharField(label="Choose a Period:", widget=forms.Select(choices=period_choices))
    date_old = forms.DateField(label="Beginning Date:", widget=DateInput, required=False)
    date_new = forms.DateField(label="Ending Date:", widget=DateInput, required=False)
