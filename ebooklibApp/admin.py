from django.contrib import admin
from .models import Book, Author, Genre

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_by', 'uploaded_at')
    exclude = ('uploaded_by',)  # Исключаем поле из формы
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Только для новых объектов
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)  # Важно: правильный отступ

admin.site.register(Book, BookAdmin)
admin.site.register(Author)
admin.site.register(Genre)