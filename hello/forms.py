from django import forms
from .models import Note
from django.core.exceptions import ValidationError
from django.conf import settings

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title','text']

class NoteFullForm(NoteForm):
    note_id = forms.IntegerField(required=False)
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={}),required=False)

    def clean_images(self):
        images = self.cleaned_data.get('images')
        print('image type:',type(images))
                
    class Meta(NoteForm.Meta):
        fields = NoteForm.Meta.fields + ['images', 'note_id']