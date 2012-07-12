from django.conf.urls.defaults import *

# for voting
from voting.views import vote_on_object
from .models import Bookmark
from .views import BookmarkList, YourBookmarks, AddBookmarkInstance, DeleteBookmarkInstance

urlpatterns = patterns('',
    url(r'^$', BookmarkList.as_view(), name="all_bookmarks"),
    url(r'^your_bookmarks/$', YourBookmarks.as_view(), name="your_bookmarks"),
    url(r'^add/$', AddBookmarkInstance.as_view(), name="add_bookmark"),
    url(r'^(\d+)/delete/$', DeleteBookmarkInstance.as_view(), name="delete_bookmark_instance"),
    
    # for voting
    (r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, dict(
            model=Bookmark,
            template_object_name='bookmark',
            template_name='kb/link_confirm_vote.html',
            allow_xmlhttprequest=True)),
)
