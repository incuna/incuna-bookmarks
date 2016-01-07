from django.contrib.sites.models import Site
from django.test import TestCase
from tagging.models import Tag

from .factories import BookmarkFactory, BookmarkInstanceFactory


class TestBookmark(TestCase):
    def test_all_tags_with_counts(self):
        tag = 'tag'
        bookmark = BookmarkFactory.create()
        bookmark.sites.add(Site.objects.get_current())
        BookmarkInstanceFactory.create(bookmark=bookmark, tags=tag)

        tags = bookmark.all_tags_with_counts()

        tag_instance = Tag.objects.get(name=tag)
        self.assertEqual(tags, [tag_instance])

    def test_all_tags_with_counts_exclude_other_bookmarks(self):
        tag = 'tag'
        other_tag = 'other'
        site = Site.objects.get_current()
        bookmark, other_bookmark = BookmarkFactory.create_batch(2)
        bookmark.sites.add(site)
        other_bookmark.sites.add(site)
        BookmarkInstanceFactory.create(bookmark=bookmark, tags=tag)
        BookmarkInstanceFactory.create(bookmark=other_bookmark, tags=other_tag)

        tags = bookmark.all_tags_with_counts()

        other_tag_instance = Tag.objects.get(name=other_tag)
        self.assertNotIn(other_tag_instance, tags)
