# -*- coding: utf-8 -*-
from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=255, widget=forms.TextInput({'class': 'form-control', 'placeholder': '虚拟机名称'}))
