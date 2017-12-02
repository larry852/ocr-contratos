from django.contrib import admin

from .models import Document


@admin.register(Document)
class AdminDocument(admin.ModelAdmin):
    list_display = ('nit', 'document', 'uploaded_at')
    actions = ['delete']
    list_display_links = None
    ordering = ('-uploaded_at',)

    def has_add_permission(self, request):
        return False

    def document(self, obj):
        name = obj.file.name.replace("input/", "").replace(".pdf", "")
        return """<a href={}> {} </a>""".format(obj.file.url, name)

    document.short_description = 'document'
    document.allow_tags = True
