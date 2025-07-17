from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Article, Category


def annotate_has_video(queryset):
    """Adds a `has_video` attribute to each article in the queryset."""
    for article in queryset:
        article.has_video = bool(article.video or article.video_url)
    return queryset


def home(request):
    query = request.GET.get('q')
    category_filter = request.GET.get('category')

    # Base queryset: only published articles
    base_qs = Article.objects.filter(published=True).order_by('-created')

    # ✅ 1. Latest Articles: Exclude trending/editor pick
    latest_qs = base_qs.filter(is_trending=False, is_editor_pick=False)
    latest_paginator = Paginator(latest_qs, 6)
    latest_page = latest_paginator.get_page(request.GET.get('latest_page'))
    latest_ids = [article.id for article in latest_page]
    latest_page = annotate_has_video(latest_page)

    # ✅ 2. Recommended Articles: Only editor pick, exclude latest
    recommended_qs = base_qs.filter(is_editor_pick=True).exclude(id__in=latest_ids)
    recommended_paginator = Paginator(recommended_qs, 6)
    recommended_page = recommended_paginator.get_page(request.GET.get('recommended_page'))
    recommended_ids = [article.id for article in recommended_page]
    recommended_page = annotate_has_video(recommended_page)

    # ✅ 3. Trending Articles: Only trending, exclude latest + recommended
    trending_qs = base_qs.filter(is_trending=True).exclude(id__in=latest_ids + recommended_ids)
    trending_paginator = Paginator(trending_qs, 6)
    trending_page = trending_paginator.get_page(request.GET.get('trending_page'))
    trending_page = annotate_has_video(trending_page)

    # ⭐ Featured Categories
    featured_categories = Category.objects.filter(is_featured=True)

    # 🔍 Search or category filter results
    if query:
        articles = base_qs.filter(Q(title__icontains=query) | Q(content__icontains=query))
        articles = annotate_has_video(articles)
    elif category_filter:
        articles = base_qs.filter(category__slug=category_filter)
        articles = annotate_has_video(articles)
    else:
        articles = annotate_has_video(base_qs[:10])

    return render(request, 'news/home.html', {
        'query': query,
        'category_filter': category_filter,
        'articles': articles,
        'latest_articles': latest_page,
        'recommended_articles': recommended_page,
        'trending_articles': trending_page,
        'featured_categories': featured_categories,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, published=True)

    # Extract embed URL for YouTube if video_url is present
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

    # rest unchanged
    related_articles = Article.objects.filter(
        category=article.category,
        published=True
    ).exclude(pk=article.pk)[:4]

    return render(request, 'news/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
    })

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles_qs = Article.objects.filter(category=category, published=True).order_by('-created')
    paginator = Paginator(articles_qs, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/category.html', {
        'category': category,
        'articles': page_obj,
        'page_obj': page_obj,
    })


