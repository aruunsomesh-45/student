from django import forms
from .models import TeacherNote

class TeacherNoteForm(forms.ModelForm):
    class Meta:
        model = TeacherNote
        fields = ['category', 'content']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'filter-select',
                'id': 'noteCategorySelect'
            }),
            'content': forms.Textarea(attrs={
                'class': 'filter-search-input',
                'rows': 4,
                'placeholder': 'Log an observation, 1-on-1 conference summary, or custom study intervention for this student...',
                'id': 'noteContentInput',
                'style': 'width: 100%; border-radius: var(--radius-md); padding: 1rem; line-height: 1.5;'
            }),
        }
