from django import template
from bookmarks.models import BookmarkInstance
from tagging.models import Tag

register = template.Library()

@register.inclusion_tag('bookmarks/tags.html')
def show_bookmarks_tags():
    """ Show a box with tags for all articles that belong to current site.
    """
    return {'bookmark_tags': Tag.objects.usage_for_queryset(queryset=BookmarkInstance.on_site.all(), counts=True, min_count=1)}