from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),  # Упрощенный путь
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),  # Упрощенный путь
    path('books/', views.books_view, name='books'),
    path('books/<int:book_id>/mark/', views.mark_book, name='mark_book'),  # Более логичный URL
    path('books/<int:book_id>/download/', views.download_book, name='download_book'),
]

# Обработка статики и медиа в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)