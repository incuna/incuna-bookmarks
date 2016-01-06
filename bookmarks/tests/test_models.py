from django.test import TestCase

from .factories import BookmarkFactory, BookmarkInstanceFactory


class TestBookmark(TestCase):
    def test_all_tags_with_counts(self):
        tag = 'tag'
        bookmark = BookmarkFactory.create()
        BookmarkInstanceFactory.create(bookmark=bookmark, tags=tag)

        tags = bookmark.all_tags_with_counts()

        self.assertIn(tag, tags)
