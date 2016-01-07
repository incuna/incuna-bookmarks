from datetime import datetime

from django.test import TestCase

from ..forms import BookmarkInstanceForm
from .factories import BookmarkFactory, UserFactory


class TestBookmarkInstanceForm(TestCase):
    def test_save(self):
        bookmark = BookmarkFactory.create()
        user = UserFactory.create()
        url = u'http://www.example.com'
        description = u'A website'
        data = {
            u'url': url,
            u'description': description,
            u'bookmark': bookmark.pk,
            u'user': user.pk,
            u'saved': datetime.now(),
        }

        form = BookmarkInstanceForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

        instance = form.save()

        self.assertEqual(instance.bookmark.url, url)
        self.assertEqual(instance.description, description)
