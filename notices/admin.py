from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_pinned", "is_published", "view_count", "created_at")
    list_filter = ("is_pinned", "is_published", "created_at")
    search_fields = ("title", "content")
    ordering = ("-is_pinned", "-created_at")
