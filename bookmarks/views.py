from datetime import datetime
import urllib2

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from bookmarks.models import Bookmark, BookmarkInstance
from bookmarks.forms import BookmarkInstanceForm


from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, BaseDetailView

def class_view_decorator(function_decorator):
    """Convert a function based decorator into a class based decorator usable
    on class based Views.

    Follows the general idea from https://docs.djangoproject.com/en/dev/topics/class-based-views/#decorating-the-class.

    Can't subclass the `View` as it breaks inheritance (super in particular),
    so we monkey-patch instead.
    """

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator

class BookmarkList(ListView):
    model = Bookmark
    context_object_name = "bookmarks"
    template_name = "bookmarks/bookmarks.html"

    def get_queryset(self):
        return Bookmark.on_site.all().order_by("-added")

    def get_context_data(self, **kwargs):
        context = super(BookmarkList, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            context.update({
                'user_bookmarks': self.get_queryset().filter(saved_instances__user=self.request.user),
                })
        return context

class BookmarkInstanceMixin(object):
    def get_queryset(self):
        return BookmarkInstance.on_site.all()

@class_view_decorator(login_required)
class YourBookmarks(BookmarkInstanceMixin, ListView):
    model = BookmarkInstance
    context_object_name = "bookmark_instances"
    template_name = "bookmarks/your_bookmarks.html"

    def get_queryset(self):
        return super(YourBookmarks, self).get_queryset().filter(user=self.request.user).order_by("-saved")

@class_view_decorator(login_required)
class AddBookmarkInstance(CreateView):
    form_class = BookmarkInstanceForm
    model = BookmarkInstance
    template_name = "bookmarks/add.html"
    
    def check_favicon(self):
        try:
            headers = {
                "Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                "Accept-Language" : "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection" : "close",
                ##"User-Agent": settings.URL_VALIDATOR_USER_AGENT
                }
            req = urllib2.Request(self.bookmark.get_favicon_url(force=True), None, headers)
            u = urllib2.urlopen(req)
            has_favicon = True
        except:
            has_favicon = False

        self.bookmark.has_favicon = has_favicon
        self.bookmark.favicon_checked = datetime.now()
        self.bookmark.save()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        self.bookmark = self.object.bookmark

        self.check_favicon()

        return HttpResponseRedirect(self.get_success_url(form.should_redirect()))

    def get_success_url(self, should_redirect=False):

            if should_redirect:
                return HttpResponseRedirect(self.bookmark.url)
            else:
                messages.info(self.request, _("You have saved bookmark '{0}'".format(self.object.description)))
                return HttpResponseRedirect(reverse("bookmarks.views.bookmarks"))

    def get_initial(self):
        initial = super(AddBookmarkInstance, self).get_initial()
        if "url" in self.request.GET:
            initial["url"] = self.request.GET["url"]
        if "description" in self.request.GET:
            initial["description"] = self.request.GET["description"].strip()
        if "redirect" in self.request.GET:
            initial["redirect"] = self.request.GET["redirect"]

        return initial

    def get_context_data(self, **kwargs):
        context = super(AddBookmarkInstance, self).get_context_data(**kwargs)

        bookmarks_add_url = "http://" + Site.objects.get_current().domain + reverse(AddBookmarkInstance)
        bookmarklet = "javascript:location.href='%s?url='+encodeURIComponent(location.href)+';description='+encodeURIComponent(document.title)+';redirect=on'" % bookmarks_add_url

        context["bookmarklet"] = bookmarklet
        return context


@class_view_decorator(login_required)
class DeleteBookmarkInstance(BookmarkInstanceMixin, BaseDetailView):

    def get_queryset(self):
        super(DeleteBookmarkInstance, self).get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.info(request, _("Successfully deleted bookmark '{0}'".format(self.object.title)))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):

        if "next" in self.request.GET:
            next = self.request.GET["next"]
        else:
            next = reverse("bookmarks.views.bookmarks")

        return next

