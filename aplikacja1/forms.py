from django import forms
from .models import Czlowiek

class CzlowiekForm(forms.ModelForm):
    class Meta:
        model = Czlowiek
        fields = ['imie', 'nazwisko']
        
    def clean(self):
        cleaned_data = super().clean()
        imie = cleaned_data.get('imie')
        nazwisko = cleaned_data.get('nazwisko')
        
        if not imie or not imie.strip():
            raise forms.ValidationError({'imie': 'First name cannot be empty'})
            
        if not nazwisko or not nazwisko.strip():
            raise forms.ValidationError({'nazwisko': 'Last name cannot be empty'})
            
        return cleaned_data