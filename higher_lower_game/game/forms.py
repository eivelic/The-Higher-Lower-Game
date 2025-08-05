from django import forms

class NicknameForm(forms.Form):
    nickname = forms.CharField(label='Unesi nadimak', max_length=50)
