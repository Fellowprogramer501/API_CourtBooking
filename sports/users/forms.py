from django import forms
from . import models 


class loginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget= forms.EmailInput(attrs={
            'class':'placeholder',
            'placeholder':'Enter email',
            'type':'email',
        })
    )
    password = forms.CharField(
        label="password",
        widget= forms.PasswordInput(attrs={
            'class':'placeholder',
            'placeholder':'Enter Password',
            # 'type':'Password',
        })
    )
class registerationform(forms.ModelForm):
    password1 = forms.CharField(
        label="password",
        widget=forms.PasswordInput(attrs={
            'class':'placeholder',
            'placeholder':'Enter Your Password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class':'placeholder',
            'placeholder':'Re-enter Your Password',
        })
    )
    class Meta:
        model = models.user
        fields = ['email','first_name','last_name','username','num']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'num': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
        # def clean(self):
        #     cleaned_data = super().clean()
        #     p1 = cleaned_data.get("password1")
        #     p2 = cleaned_data.get("password2")
        #     if p1 and p2 and p1 != p2:
        #         raise forms.ValidationError("Passwords doesnot match")
        #     return cleaned_data
        def clean(self):
            cleaned_data = super().clean()
            p1 = cleaned_data.get("password1")
            p2 = cleaned_data.get("password2")
            if p1 and p2 and p1 != p2:
                raise forms.ValidationError("Passwords do not match.")
            return cleaned_data
        
        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.data["password1"])
            if commit:
                user.save()
            return user
            
            