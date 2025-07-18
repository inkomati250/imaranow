from django import template
from django.utils.timezone import now
import re

register = template.Library()

@register.filter
def posted_ago(value):
    """
    Returns a string like:
    - 'X years ago' if >= 365 days
    - 'X months ago' if >= 30 days
    - 'X days ago' if 1 day or more
    - 'X hours ago' if less than a day
    - 'X minutes ago' if less than an hour
    - 'Just now' if less than a minute
    """
    if not value:
        return ""

    delta = now() - value
    total_seconds = delta.total_seconds()
    days = delta.days
    hours = int(total_seconds // 3600)
    minutes = int(total_seconds // 60)

    if days >= 365:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif days >= 30:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif days >= 1:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours >= 1:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

@register.filter
def youtube_id(url):
    pattern = r"(?:v=|youtu\.be/|embed/)([\w-]{11})"
    match = re.search(pattern, url or "")
    return match.group(1) if match else None

