from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import FileResponse, Http404
from django.core.cache import cache
from django.conf import settings
from .models import Book, Genre, Author, Profile
from .forms import BookForm, ProfileForm
import os
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Главная страница с интеллектуальным редиректом"""
    if request.user.is_authenticated:
        return redirect('books')
    return render(request, 'ebooklibApp/home.html')

def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('books')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'ebooklibApp/registration/register.html', {'form': form})

def login_view(request):
    """Аутентификация пользователя"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('books')
        messages.error(request, 'Неверные имя пользователя или пароль')
    else:
        form = AuthenticationForm()
    return render(request, 'ebooklibApp/registration/login.html', {'form': form})

@login_required
def profile_view(request):
    """Профиль пользователя с избранными книгами"""
    profile = request.user.profile
    marked_books = Book.objects.filter(marked_by=request.user).select_related('author')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'ebooklibApp/profile.html', {
        'profile': profile,
        'marked_books': marked_books,
        'form': form
    })

def get_cache_key(params):
    # Упрощаем ключ и ограничиваем длину
    key = f"books_{params['user_id']}_{params['title'][:10]}_{params['author'][:10]}_{params['genre'][:10]}"
    return md5(key.encode()).hexdigest()  # Хешируем для гарантированной длины

@login_required
def books_view(request):
    """Список книг с работающей пагинацией при поиске"""
    # Получаем параметры поиска
    search_params = {
        'title': request.GET.get('title', '').strip(),
        'author': request.GET.get('author', '').strip(),
        'genre': request.GET.get('genre', '').strip()
    }
    
    # Базовый запрос
    books = Book.objects.all().order_by('title')
    
    # Применяем фильтры
    if search_params['title']:
        books = books.filter(title__icontains=search_params['title'])
    if search_params['author']:
        books = books.filter(author__name__icontains=search_params['author'])
    if search_params['genre']:
        books = books.filter(genres__name__icontains=search_params['genre'])
    
    # Пагинация с сохранением параметров поиска
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Добавляем параметры поиска в paginator
    if any(search_params.values()):
        for page_num in page_obj.paginator.page_range:
            page_obj.paginator.page(page_num).search_params = search_params
    
    # Форма добавления книги
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user
            book.save()
            form.save_m2m()
            messages.success(request, 'Книга успешно добавлена!')
            return redirect('books')
    else:
        form = BookForm()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'genres': Genre.objects.all(),
        'title_query': search_params['title'],
        'author_query': search_params['author'],
        'genre_query': search_params['genre'],
    }
    
    return render(request, 'ebooklibApp/books.html', context)


@login_required
def download_book(request, book_id):
    """Скачивание книги с проверкой доступности файла"""
    book = get_object_or_404(Book, id=book_id)
    
    if not book.file:
        messages.error(request, 'Файл книги недоступен')
        return redirect('books')
    
    try:
        response = FileResponse(book.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(book.file.name)}"'
        book.downloads += 1
        book.save()
        return response
    except Exception as e:
        logger.error(f"File download error: {str(e)}")
        messages.error(request, 'Ошибка при скачивании файла')
        return redirect('books')

@login_required
def mark_book(request, book_id):
    """Добавление/удаление книги из избранного"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.user in book.marked_by.all():
        book.marked_by.remove(request.user)
        messages.success(request, 'Книга удалена из избранного')
    else:
        book.marked_by.add(request.user)
        messages.success(request, 'Книга добавлена в избранное')
    
    return redirect(request.META.get('HTTP_REFERER', 'books'))

@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('home')

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            if request.user.is_authenticated:
                book.uploaded_by = request.user
            book.save()
            form.save_m2m()  # Для сохранения ManyToMany
            return redirect('book_list')  # Замените на ваш URL
    else:
        form = BookForm()
    
    return render(request, 'ebooklibApp/add_book.html', {'form': form})