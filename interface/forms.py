from django import forms

class DatabaseConnectionForm(forms.Form):
    host = forms.CharField()
    username = forms.CharField()
    password = forms.CharField()
    dbname = forms.CharField()

