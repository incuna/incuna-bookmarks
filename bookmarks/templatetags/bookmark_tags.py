from django import template
from bookmarks.models import BookmarkInstance
from tagging.models import Tag

register = template.Library()

@register.inclusion_tag('bookmarks/tags.html')
def show_bookmarks_tags():
    """ Show a box with tags for all articles that belong to current site.
    """
    return {'bookmark_tags': Tag.objects.usage_for_queryset(queryset=BookmarkInstance.on_site.all(), counts=True, min_count=1)}


class BookmarkInstances(template.Node):
    def __init__(self, user, limit, var_name):
        self.limit = limit
        self.var_name = var_name

        self.user = user
        if user:
            self.user = template.Variable(user)

    def render(self, context):
        if self.user:
             # resolve the (variable) arguments in context
            user = self.user.resolve(context)
            bookmark_instances = BookmarkInstance.on_site.filter(user=user).order_by("-saved")[:int(self.limit)]
        else:
            bookmark_instances = BookmarkInstance.on_site.all().order_by("-saved")[:int(self.limit)]

        if (int(self.limit) == 1):
            context[self.var_name] = bookmark_instances[0]
        else:
            context[self.var_name] = bookmark_instances
        return ''


def do_recent_bookmarks(parser, token):
    """
    Retrieves ``num`` bookmark instances on current site
    and stores them in a specified context variable.

    Syntax::
        {% recent_bookmarks [num] as [varname] %}

    Example::
        {% recent_bookmarks 5 as bookmarks %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return BookmarkInstances(None, bits[1], bits[3])

def do_recent_bookmarks_for(parser, token):
    """
    Retrieves ``num`` bookmark instances on current site
    and stores them in a specified context variable.

    Syntax::
        {% recent_bookmarks [num] as [varname] %}

    Example::
        {% recent_bookmarks 5 as bookmarks %}
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits[3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return BookmarkInstances(bits[1], bits[2], bits[4])


register.tag('recent_bookmarks', do_recent_bookmarks)
register.tag('recent_bookmarks_for', do_recent_bookmarks_for)