import urlparse

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from tagging.models import Tag

"""
A Bookmark is unique to a URL whereas a BookmarkInstance represents a
particular Bookmark saved by a particular person.

This not only enables more than one user to save the same URL as a
bookmark but allows for per-user tagging.
"""

# at the moment Bookmark has some fields that are determined by the
# first person to add the bookmark (the adder) but later we may add
# some notion of voting for the best description and note from
# amongst those in the instances.

# Manager for bookmarks only returns those that belong to current site.
class LiveBookmarkManager(models.Manager):
    def get_queryset(self):
        current_site = Site.objects.get_current()
        return super(LiveBookmarkManager, self).get_queryset().filter(sites=current_site)


class Bookmark(models.Model):
    url = models.URLField(max_length=511)
    description = models.TextField(_('description'))
    note = models.TextField(_('note'), blank=True)

    has_favicon = models.BooleanField(_('has favicon'), default=False)
    favicon_checked = models.DateTimeField(_('favicon checked'), default=timezone.now)

    adder = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="added_bookmarks", verbose_name=_('adder'))
    added = models.DateTimeField(_('added'), default=timezone.now)

    sites = models.ManyToManyField(Site)

    objects = models.Manager()  # The default manager.
    on_site = LiveBookmarkManager()

    def get_favicon_url(self, force=False):
        """
        return the URL of the favicon (if it exists) for the site this
        bookmark is on other return None.

        If force=True, the URL will be calculated even if it doesn't
        exist.
        """
        if self.has_favicon or force:
            base_url = '%s://%s' % urlparse.urlsplit(self.url)[:2]
            favicon_url = urlparse.urljoin(base_url, 'favicon.ico')
            return favicon_url
        return None

    def all_tags(self, min_count=False):
        return Tag.objects.usage_for_queryset(BookmarkInstance.on_site.all(), counts=False, min_count=None, filters={'bookmark': self.id})

    def all_tags_with_counts(self, min_count=False):
        return Tag.objects.usage_for_queryset(
            BookmarkInstance.on_site.filter(bookmark=self.pk),
            counts=True,
            min_count=None,
        )

    def site_slugs(self):
        slugs = []
        for site in self.sites.all():
            slugs.append(site.ghtsite.slug)
        return ' '.join(slugs)

    def __unicode__(self):
        return self.url

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(Bookmark, self).save(force_insert, force_update, *args, **kwargs)
        if not self.sites:
            current_site = Site.objects.get_current()
            self.sites.add(current_site)

    class Meta:
        ordering = ('-added',)


# Manager for bookmark instances only returns those that belong to current site.
class LiveBookmarkInstanceManager(models.Manager):
    def get_queryset(self):
        current_site = Site.objects.get_current()
        return super(LiveBookmarkInstanceManager, self).get_queryset().filter(bookmark__sites=current_site).distinct()


class BookmarkInstance(models.Model):
    bookmark = models.ForeignKey(Bookmark, related_name="saved_instances", verbose_name=_('bookmark'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="saved_bookmarks", verbose_name=_('user'))
    saved = models.DateTimeField(_('saved'), default=timezone.now)

    description = models.TextField(_('description'))
    note = models.TextField(_('note'), blank=True)

    tags = TagField()

    objects = models.Manager()  # The default manager.
    on_site = LiveBookmarkInstanceManager()

    def get_or_create_bookmark(self, url):
        try:
            bookmark = Bookmark.on_site.get(url=url)
        except Bookmark.DoesNotExist:
            # has_favicon=False is temporary as the view for adding bookmarks will change it
            bookmark = Bookmark(
                url=url,
                description=self.description,
                note=self.note,
                has_favicon=False,
                adder=self.user,
            )
            bookmark.save()
            bookmark.sites.add(Site.objects.get_current())
        return bookmark

    def delete(self):
        bookmark = self.bookmark
        super(BookmarkInstance, self).delete()
        if bookmark.saved_instances.all().count() == 0:
            bookmark.delete()

    def __unicode__(self):
        return _("%(bookmark)s for %(user)s") % {'bookmark':self.bookmark, 'user':self.user}
