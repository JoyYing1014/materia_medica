from django import forms
from .models import Images
class UploadImageForm(forms.ModelForm):
    '''图像上传表单'''
    class Meta:
        model = Images
        fields = ['photo']