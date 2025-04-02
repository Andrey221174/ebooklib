# ebooklib/forms.py
from django import forms
from .models import Book, Profile, Author, Genre

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genres', 'pdf']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()
        self.fields['genres'].queryset = Genre.objects.all()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']