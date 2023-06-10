from django import forms

class ProductNameFilterForm(forms.Form):
    name = forms.CharField()