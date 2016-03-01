from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from bookmarks.models import Bookmark, BookmarkInstance
from bookmarks.forms import BookmarkInstanceForm


def bookmarks(request, template_name="bookmarks/bookmarks.html"):
    bookmarks = Bookmark.on_site.all().order_by("-added")
    if request.user.is_authenticated():
        user_bookmarks = Bookmark.on_site.filter(saved_instances__user=request.user)
    else:
        user_bookmarks = []
    return render_to_response(template_name, {
        "bookmarks": bookmarks,
        "user_bookmarks": user_bookmarks,
    }, context_instance=RequestContext(request))


@login_required
def your_bookmarks(request, template_name="bookmarks/your_bookmarks.html"):
    bookmark_instances = BookmarkInstance.on_site.filter(user=request.user)
    bookmark_instances = bookmark_instances.order_by("-saved")
    return render_to_response(template_name, {
        "bookmark_instances": bookmark_instances,
    }, context_instance=RequestContext(request))


@login_required
def add(request, form_class=BookmarkInstanceForm,
        template_name="bookmarks/add.html"):

    if request.method == "POST":
        bookmark_form = form_class(request.user, request.POST)
        if bookmark_form.is_valid():
            bookmark_instance = bookmark_form.save(commit=False)
            bookmark_instance.user = request.user
            bookmark_instance.save()
            bookmark = bookmark_instance.bookmark

            bookmark.has_favicon = False
            bookmark.favicon_checked = timezone.now()
            bookmark.save()

            if bookmark_form.should_redirect():
                return HttpResponseRedirect(bookmark.url)
            else:
                message = _("You have saved bookmark '{}'")
                message = message.format(bookmark_instance.description)
                messages.info(request, message)
                return HttpResponseRedirect(reverse("bookmarks.views.bookmarks"))
    else:
        initial = {}
        if "url" in request.GET:
            initial["url"] = request.GET["url"]
        if "description" in request.GET:
            initial["description"] = request.GET["description"].strip()
        if "redirect" in request.GET:
            initial["redirect"] = request.GET["redirect"]

        if initial:
            bookmark_form = form_class(initial=initial)
        else:
            bookmark_form = form_class()

    bookmarks_add_url = "http://" + Site.objects.get_current().domain + reverse(add)
    bookmarklet = ';'.join((
        "javascript:location.href='{}?url='+encodeURIComponent(location.href)+'",
        "description='+encodeURIComponent(document.title)+'",
        "redirect=on'",
    )).format(bookmarks_add_url)

    return render_to_response(
        template_name,
        {"bookmarklet": bookmarklet, "bookmark_form": bookmark_form},
        context_instance=RequestContext(request))


@login_required
def delete(request, bookmark_instance_id):
    bookmark_instance = get_object_or_404(
        BookmarkInstance.on_site.all(),
        id=bookmark_instance_id,
    )
    if request.user == bookmark_instance.user:
        bookmark_instance.delete()
        message = _("You have deleted bookmark '{}'")
        message = message.format(bookmark_instance.description)
        messages.info(request, message)

    if "next" in request.GET:
        next = request.GET["next"]
    else:
        next = reverse("bookmarks.views.bookmarks")

    return HttpResponseRedirect(next)
