from django.db import models
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.utils.text import slugify
from taggit.managers import TaggableManager

# ---------------------------
# Categories
# ---------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)  # Show on homepage nav?

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------------------------
# Articles
# ---------------------------
class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.CharField(max_length=100, default="Staff Reporter")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    summary = models.TextField(blank=True, null=True)  # For card preview
    content = RichTextField()

    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(500, 300)],
        format='JPEG',
        options={'quality': 85}
    )

    # 🎥 Media support
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Paste YouTube/Vimeo embed URL")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    is_trending = models.BooleanField(default=False)
    is_editor_pick = models.BooleanField(default=False)
    published = models.BooleanField(default=True)

    tags = TaggableManager(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ---------------------------
# Authors
# ---------------------------
class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)  # e.g., {"twitter": "...", "facebook": "..."}

    def __str__(self):
        return self.name


# ---------------------------
# Subscribers
# ---------------------------
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# ---------------------------
# Static / Legal / Company Pages
# ---------------------------
class Page(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    content = RichTextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# ---------------------------
# Social Links
# ---------------------------
class SocialLink(models.Model):
    name = models.CharField(max_length=50)  # e.g., Facebook
    url = models.URLField()
    icon_svg = models.TextField(blank=True)  # optional for custom SVG
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name




