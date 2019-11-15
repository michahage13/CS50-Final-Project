from django import forms
from datetime import date

from .models import macros

class macrosForm(forms.ModelForm):
    date    = forms.DateField(label="Meal date", initial=date.today,
                widget=forms.DateInput(attrs={"class":"meal-date", "type":"date"}))
    protein = forms.IntegerField(label="Protein consumed", initial=100,
                widget=forms.NumberInput(attrs={"class":"protein"}))
    fat = forms.IntegerField(label="Fat consumed", initial=100,
                widget=forms.NumberInput(attrs={"class":"fat"}))
    carbohydrates = forms.IntegerField(label="Carbohydrates consumed", initial=0,
                widget=forms.NumberInput(attrs={"class":"carbs"}))
    cheat = forms.BooleanField(label="Do you consider it a cheat meal?", required=False,
                widget=forms.CheckboxInput(attrs={"class":"cheat"}))
    comment = forms.CharField(label="Describe shortly what your meal was", required=False,
                widget=forms.TextInput(attrs={"class":"comment"}))
    description = forms.CharField(label="Optional detailed description", required=False,
                widget=forms.Textarea(attrs={"class":"description"}))
    image = forms.ImageField(label="Upload a picture of your meal", required=False,
                widget=forms.ClearableFileInput(attrs={"class":"image"}))

    class Meta:
        model = macros
        fields = [
            'protein',
            'fat',
            'carbohydrates',
            'date',
            'cheat',
            'comment',
            'description',
            'image'
        ]
