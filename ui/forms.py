from django import forms
from core.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['cara_token']
        widgets = {
            'cara_token': forms.TextInput(attrs={'class': 'form-control'})
        }