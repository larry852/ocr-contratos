from django.contrib import admin

from .models import Document


@admin.register(Document)
class AdminDocument(admin.ModelAdmin):
    list_display = ('nit', 'file', 'uploaded_at')
