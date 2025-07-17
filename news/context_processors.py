from .models import Category

def featured_categories(request):
    return {
        'featured_categories': Category.objects.filter(is_featured=True)
    }
