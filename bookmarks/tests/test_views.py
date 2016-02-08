from django.core.urlresolvers import reverse
from django_webtest import WebTest

from ..models import BookmarkInstance
from .factories import BookmarkFactory, UserFactory


class TestAddBookmark(WebTest):
    def test_add(self):
        bookmark = BookmarkFactory.create()
        user = UserFactory.create()
        view_url = reverse('add_bookmark')

        url = 'https://example.com'
        description = 'My bookmark'

        form = self.app.get(view_url, user=user).form
        form['bookmark'] = bookmark.pk
        form['url'] = url
        form['user'] = user.pk
        form['description'] = description

        response = form.submit(user=user)
        self.assertEqual(response.status_code, 302)

        instance = BookmarkInstance.objects.get()
        self.assertEqual(instance.bookmark.url, url)
        self.assertEqual(instance.user, user)
        self.assertEqual(instance.description, description)
