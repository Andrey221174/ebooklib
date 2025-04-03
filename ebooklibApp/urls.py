# ebooklib/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('home/register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/profile/', views.profile_view, name='profile'),
    path('books/', views.books_view, name='books'),
    path('mark/<int:book_id>/', views.mark_book, name='mark_book'),
    path('book/<int:book_id>/download/', views.download_book, name='download_book'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)