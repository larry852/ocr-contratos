from django.contrib import admin

from .models import Document
from . import utils

from . import reporter


@admin.register(Document)
class AdminDocument(admin.ModelAdmin):
    list_display = ('nit', 'document', 'uploaded_at', 'analysis')
    actions = ['delete', 'reporter']
    list_display_links = None
    ordering = ('-uploaded_at',)

    def has_add_permission(self, request):
        return False

    def document(self, obj):
        return """<a target="_blank" href={}> {} </a>""".format(obj.file.url, utils.get_name_document(obj))

    document.short_description = 'document'
    document.allow_tags = True

    def analysis(self, obj):
        return """<a target="_blank" href=/{}> Analysis </a>""".format(obj.id)

    analysis.short_description = 'analysis'
    analysis.allow_tags = True

    def reporter(self, request, queryset):
        return reporter.generate(queryset)

    reporter.short_description = "Generate report"
