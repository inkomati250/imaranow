from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince
from django.utils.timezone import now

from .models import Article, Category, Subscriber


def annotate_has_video(queryset):
    """Add a 'has_video' boolean attribute to articles for template logic."""
    for article in queryset:
        article.has_video = bool(article.video or article.video_url)
    return queryset


def get_sidebar_context():
    """Fetch data for sidebar: most viewed articles and latest videos."""
    most_viewed = Article.objects.filter(published=True).order_by('-views')[:5]
    latest_videos = Article.objects.filter(
        published=True
    ).filter(
        Q(video_url__isnull=False) | Q(video__isnull=False)
    ).order_by('-created')[:5]

    most_viewed = annotate_has_video(most_viewed)
    latest_videos = annotate_has_video(latest_videos)

    # Add formatted views for display
    for article in most_viewed:
        article.views_display = f"{article.views:,}"  # comma-separated

    # Add hours ago attribute for videos
    for video in latest_videos:
        delta = now() - video.created
        hours_ago = int(delta.total_seconds() // 3600)
        video.hours_ago = hours_ago if hours_ago > 0 else "<1"

    return {
        'most_viewed': most_viewed,
        'latest_videos': latest_videos,
    }


def home(request):
    query = request.GET.get('q')
    category_filter = request.GET.get('category')
    base_qs = Article.objects.filter(published=True).order_by('-created')

    # Latest Articles
    latest_qs = base_qs.filter(is_trending=False, is_editor_pick=False)
    latest_paginator = Paginator(latest_qs, 6)
    latest_page = latest_paginator.get_page(request.GET.get('latest_page'))
    latest_ids = [article.id for article in latest_page]
    latest_page = annotate_has_video(latest_page)

    # Recommended Articles
    recommended_qs = base_qs.filter(is_editor_pick=True).exclude(id__in=latest_ids)
    recommended_paginator = Paginator(recommended_qs, 6)
    recommended_page = recommended_paginator.get_page(request.GET.get('recommended_page'))
    recommended_ids = [article.id for article in recommended_page]
    recommended_page = annotate_has_video(recommended_page)

    # Trending Articles
    trending_qs = base_qs.filter(is_trending=True).exclude(id__in=latest_ids + recommended_ids)
    trending_paginator = Paginator(trending_qs, 6)
    trending_page = trending_paginator.get_page(request.GET.get('trending_page'))
    trending_page = annotate_has_video(trending_page)

    featured_categories = Category.objects.filter(is_featured=True)

    # Search or category filter
    if query:
        articles = base_qs.filter(Q(title__icontains=query) | Q(content__icontains=query))
    elif category_filter:
        articles = base_qs.filter(category__slug=category_filter)
    else:
        articles = base_qs[:10]

    articles = annotate_has_video(articles)

    context = {
        'query': query,
        'category_filter': category_filter,
        'articles': articles,
        'latest_articles': latest_page,
        'recommended_articles': recommended_page,
        'trending_articles': trending_page,
        'featured_categories': featured_categories,
    }

    context.update(get_sidebar_context())
    return render(request, 'news/home.html', context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, published=True)

    # Increment views count by 1 on each visit
    article.views = article.views + 1
    article.save(update_fields=['views'])

    # Extract YouTube embed URL
    video_embed_url = None
    if article.video_url and "youtube.com/watch" in article.video_url:
        import urllib.parse as urlparse
        from urllib.parse import parse_qs
        url_data = urlparse.urlparse(article.video_url)
        query = parse_qs(url_data.query)
        video_id = query.get("v")
        if video_id:
            video_embed_url = f"https://www.youtube.com/embed/{video_id[0]}"

    article.video_embed_url = video_embed_url
    article.has_video = bool(article.video or article.video_url)

    related_articles = Article.objects.filter(
        category=article.category,
        published=True
    ).exclude(pk=article.pk)[:4]

    context = {
        'article': article,
        'related_articles': related_articles,
    }
    context.update(get_sidebar_context())

    return render(request, 'news/article_detail.html', context)


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles_qs = Article.objects.filter(category=category, published=True).order_by('-created')
    paginator = Paginator(articles_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'articles': page_obj,
        'page_obj': page_obj,
        'featured_categories': Category.objects.filter(is_featured=True),
    }
    context.update(get_sidebar_context())

    return render(request, 'news/category.html', context)


@require_POST
def subscribe(request):
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'error': 'Invalid email format'}, status=400)

    # Prevent duplicates
    if not Subscriber.objects.filter(email=email).exists():
        Subscriber.objects.create(email=email)

    return JsonResponse({'message': f'Subscribed {email} successfully!'})




