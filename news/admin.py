from django.contrib import admin
from .models import Category, Article
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured')
    list_filter = ('is_featured',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created', 'published', 'is_trending', 'is_editor_pick', 'thumbnail_preview')
    list_filter = ('category', 'published', 'is_trending', 'is_editor_pick', 'created')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'thumbnail_preview')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category', 'summary', 'content')
        }),
        ('Media', {
            'fields': ('image', 'video_url', 'video', 'thumbnail_preview')
        }),
        ('Meta', {
            'fields': ('tags', 'is_trending', 'is_editor_pick', 'published', 'views')
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 80px; object-fit: cover;" />', obj.image.url)
        return "-"
    thumbnail_preview.short_description = "Thumbnail"


