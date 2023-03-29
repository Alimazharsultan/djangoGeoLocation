from django import forms
from .models import Measurement, UnitrackInput

class MeasurementModelForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ('destination',)

class Locationfields(forms.ModelForm):
    class Meta:
        labels = {'date_time_input':"Date and Time Format: MM/DD/YY hh:mm:ss"}
        model = UnitrackInput
        fields= ('date_time_input',)