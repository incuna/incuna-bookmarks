from datetime import datetime
import urlparse
import urllib2

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

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
    bookmark_instances = BookmarkInstance.on_site.filter(user=request.user).order_by("-saved")
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
            
            try:
                headers = {
                    "Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                    "Accept-Language" : "en-us,en;q=0.5",
                    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                    "Connection" : "close",
                    ##"User-Agent": settings.URL_VALIDATOR_USER_AGENT
                    }
                req = urllib2.Request(bookmark.get_favicon_url(force=True), None, headers)
                u = urllib2.urlopen(req)
                has_favicon = True
            except:
                has_favicon = False
            
            bookmark.has_favicon = has_favicon
            bookmark.favicon_checked = datetime.now() 
            bookmark.save()
            
            if bookmark_form.should_redirect():
                return HttpResponseRedirect(bookmark.url)
            else:
                request.user.message_set.create(message=_("You have saved bookmark '%(description)s'") % {'description': bookmark_instance.description})
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
    bookmarklet = "javascript:location.href='%s?url='+encodeURIComponent(location.href)+';description='+encodeURIComponent(document.title)+';redirect=on'" % bookmarks_add_url
    
    return render_to_response(template_name, {
        "bookmarklet": bookmarklet,
        "bookmark_form": bookmark_form,
    }, context_instance=RequestContext(request))

@login_required
def delete(request, bookmark_instance_id):
    
    bookmark_instance = get_object_or_404(BookmarkInstance.on_site.all(), id=bookmark_instance_id)
    if request.user == bookmark_instance.user:
        #BookmarkInstance.objects.get(pk=bookmark_instance_id, user=request.user).delete()
        bookmark_instance.delete()
    
        request.user.message_set.create(message=_("You have deleted bookmark '%(description)s'") % {'description': bookmark_instance.description})

    
    if "next" in request.GET:
        next = request.GET["next"]
    else:
        next = reverse("bookmarks.views.bookmarks")
    
    return HttpResponseRedirect(next)
    