from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Book, Genre, Author, Profile
from .forms import BookForm, ProfileForm

def home(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.profile
    marked_books = request.user.marked_books.all()
    return render(request, 'profile.html', {
        'profile': profile,
        'marked_books': marked_books
    })

@login_required
def books_view(request):
    books = Book.objects.all()
    genres = Genre.objects.all()
    authors = Author.objects.all()
    
    # Фильтрация
    title_query = request.GET.get('title')
    author_query = request.GET.get('author')
    genre_query = request.GET.get('genre')
    
    if title_query:
        books = books.filter(title__icontains=title_query)
    if author_query:
        books = books.filter(author__name__icontains=author_query)
    if genre_query:
        books = books.filter(genres__name__icontains=genre_query)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user
            book.save()
            form.save_m2m()
            return redirect('books')
    else:
        form = BookForm()
    
    return render(request, 'books.html', {
        'books': books,
        'genres': genres,
        'authors': authors,
        'form': form
    })

@login_required
def mark_book(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.user in book.marked_by.all():
        book.marked_by.remove(request.user)
    else:
        book.marked_by.add(request.user)
    return redirect('books')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')