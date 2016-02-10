from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

# for voting
from voting.views import vote_on_object
from bookmarks.models import Bookmark
from bookmarks import views

urlpatterns = [
    url(r'^$', views.bookmarks, name="all_bookmarks"),
    url(r'^your_bookmarks/$', views.your_bookmarks, name="your_bookmarks"),
    url(r'^add/$', views.add, name="add_bookmark"),
    url(r'^(\d+)/delete/$', views.delete, name="delete_bookmark_instance"),

    # for voting
    url(
        r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        csrf_exempt(vote_on_object),
        {
            'model': Bookmark,
            'template_object_name': 'bookmark',
            'template_name': 'kb/link_confirm_vote.html',
            'allow_xmlhttprequest': True,
        },
    ),
]
