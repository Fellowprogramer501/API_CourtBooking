from django import forms
from .models import Court, booking_order, Sport, Branch
from datetime import datetime,timezone

class BookingForm(forms.ModelForm):
    class Meta:
        model = booking_order
        fields = ['Date', 'time', 'duration','branch','sport']
        widgets = {
            'Date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.TimeInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'sport': forms.Select(attrs={'class': 'form-control'}),
        }
        def clean(self):
            cleaned_data = super().clean()
            branch = cleaned_data.get('branch')
            sport = cleaned_data.get('sport')
            
            if branch and sport :
                court = Court.objects.filter(branch=branch,sport=sport).first()
                if not court:
                    raise forms.ValidationError(
                        f"no court for branch'{branch}' and sport {sport}"
                    )
            return cleaned_data
        
        def save(self, commit=True):
            sv = super().save(commit=False)
            
            branch = self.cleaned_data.get('branch')
            sport = self.cleaned_data.get('sport')
            start = self.cleaned_date.get('start')
            
            court = Court.objects.objects.filter(branch=branch, sport=sport)
            
            sv.court = court
            if start <= timezone.now:
                raise forms.ValidationError("the selected time invalid")
            if commit:
                sv.save()
            return sv

class court_selection(forms.ModelForm):
    class Meta:
        model = booking_order
        fields = ['court_no']
        widgets = {
            'court_no': forms.NumberInput(attrs={'class': 'form-control'})
        }
        def save(self, commit=True):
            sv = super().save(commit=False)
            if commit:
                sv.save()
            return sv
        