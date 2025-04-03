from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Book, Genre, Author, Profile
from .forms import BookForm, ProfileForm
from django.contrib.auth import login
from django.contrib import messages  # Добавьте этот импорт
from django.core.paginator import Paginator

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')  # Убедитесь что 'profile' - правильное имя URL
        else:
            # Добавьте отладочную информацию
            print("Ошибки формы:", form.errors)
            messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = UserCreationForm()
    
    return render(request, 'ebooklibApp/registration/register.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'ebooklibApp/home.html')

# def register_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('profile')
#     else:
#         form = UserCreationForm()
#     return render(request, 'ebooklibApp/registration/register.html', {'form': form})

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
    return render(request, 'ebooklibApp/registration/login.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.profile
    marked_books = request.user.marked_books.all()  # Теперь это будет работать
    return render(request, 'ebooklibApp/profile.html', {
        'profile': profile,
        'marked_books': marked_books
    })

# @login_required
def books_view(request):
    # Получение и фильтрация книг
    books = Book.objects.all().select_related('author').prefetch_related('genres')
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
    
    # Пагинация
    paginator = Paginator(books, 10)  # 10 книг на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Обработка формы
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                book = form.save(commit=False)
                book.uploaded_by = request.user
                book.save()
                # Для ManyToMany сохраняем после основного объекта
                form.save_m2m()
                messages.success(request, 'Книга успешно добавлена!')
                return redirect('books')
            except Exception as e:
                messages.error(request, f'Ошибка при загрузке книги: {str(e)}')
        else:
            messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = BookForm()
    
    return render(request, 'ebooklibApp/books.html', {
        'page_obj': page_obj,
        'genres': genres,
        'authors': authors,
        'form': form,
        'title_query': title_query or '',
        'author_query': author_query or '',
        'genre_query': genre_query or '',
    })

# @login_required
# def books_view(request):
#     books = Book.objects.all()
#     genres = Genre.objects.all()
#     authors = Author.objects.all()
    
#     # Фильтрация
#     title_query = request.GET.get('title')
#     author_query = request.GET.get('author')
#     genre_query = request.GET.get('genre')
    
#     if title_query:
#         books = books.filter(title__icontains=title_query)
#     if author_query:
#         books = books.filter(author__name__icontains=author_query)
#     if genre_query:
#         books = books.filter(genres__name__icontains=genre_query)
    
#     if request.method == 'POST':
#         form = BookForm(request.POST, request.FILES)
#         if form.is_valid():
#             book = form.save(commit=False)
#             book.uploaded_by = request.user
#             book.save()
#             form.save_m2m()
#             return redirect('books')
#     else:
#         form = BookForm()
    
#     return render(request, 'ebooklibApp/books.html', {
#         'books': books,
#         'genres': genres,
#         'authors': authors,
#         'form': form
#     })

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