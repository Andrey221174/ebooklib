from django import forms
from .models import Book, Author, Genre, Profile

class BookForm(forms.ModelForm):
    new_author = forms.CharField(max_length=200, required=False, label="Добавить нового автора")
    new_genre = forms.CharField(max_length=100, required=False, label="Добавить новый жанр")
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'genres', 'pdf', 'new_author', 'new_genre']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['genres'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        author = cleaned_data.get('author')
        new_author = cleaned_data.get('new_author')
        
        if not author and not new_author:
            raise forms.ValidationError("Необходимо указать автора или добавить нового")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Обработка нового автора
        new_author = self.cleaned_data.get('new_author')
        if new_author:
            author, created = Author.objects.get_or_create(name=new_author)
            instance.author = author
        
        if commit:
            instance.save()
            self.save_m2m()  # Для сохранения ManyToMany полей
        
        # Обработка нового жанра
        new_genre = self.cleaned_data.get('new_genre')
        if new_genre:
            genre, created = Genre.objects.get_or_create(name=new_genre)
            instance.genres.add(genre)
        
        return instance
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']