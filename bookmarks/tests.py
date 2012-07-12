from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client, RequestFactory

from .models import Bookmark, BookmarkInstance
from .views import BookmarkList, YourBookmarks
from voting.models import Vote

import factory

class UserFactory(factory.Factory):
    FACTORY_FOR = User

class SiteFactory(factory.Factory):
    FACTORY_FOR = Site

    domain = factory.Sequence(lambda x: 'testsite{0}'.format(x))
    name = factory.Sequence(lambda x: 'testsite{0}'.format(x))


class BookmarkFactory(factory.Factory):
    FACTORY_FOR = Bookmark

    url = factory.Sequence(lambda x: 'http://incuna.com/{0}'.format(x))
    description = "Experts in digital healthcare"
    note = "Note!"

class BookmarkInstanceFactory(factory.Factory):
    FACTORY_FOR = BookmarkInstance

class BaseBookmarksTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User(username='user')
        cls.user.set_password('pass')
        cls.user.raw_password = 'pass'

    def set_current_site(self):

        self.current_site = SiteFactory()
        self.old_site_id = settings.SITE_ID
        settings.SITE_ID = self.current_site.id

    def setUp(self):
        self.client = Client()
        self.user.save()

        self.set_current_site()

        self.request = HttpRequest()

    def tearDown(self):
        settings.SITE_ID = self.old_site_id


class BookmarkListMixin(object):
    pass
        
class BookmarkListPageTests(BookmarkListMixin, BaseBookmarksTests):

    def test_bookmarklist_onsite(self):
        " Only Bookmarks from current site appear on the list "

        bookmark = BookmarkFactory(adder=self.user)
        bookmark.sites.add(self.current_site)

        bookmark_other_site = BookmarkFactory(adder=self.user)
        bookmark_other_site.sites.add(SiteFactory())

        view_instance = BookmarkList()
        queryset = view_instance.get_queryset()
        self.assertTrue(bookmark in queryset)
        self.assertFalse(bookmark_other_site in queryset)


    def test_not_logged_in(self):
        " No user_bookmarks in context "
        bookmark = BookmarkFactory(adder=self.user)
        bookmark.sites.add(self.current_site)
        instance = BookmarkInstanceFactory(bookmark=bookmark, user=self.user)

        # user is not logged in
        self.request.user = AnonymousUser()

        view_instance = BookmarkList(**{'request':self.request})
        self.assertFalse('user_bookmarks' in view_instance.get_context_data(object_list=view_instance.get_queryset()).keys())

    def test_logged_in(self):
        " user_bookmarks contain only this user "

        # Bookmark belongs to self.user
        bookmark = BookmarkFactory(adder=self.user)
        bookmark.sites.add(self.current_site)

        # another_user logs in.
        self.request.user = another_user = UserFactory()
        # He does not have any bookmark instances saved
        view_instance = BookmarkList(**{'request':self.request})
        context = view_instance.get_context_data(object_list=view_instance.get_queryset())
        self.assertFalse(bookmark in context['user_bookmarks'])

        # another user saves BookmarkInstance
        instance = BookmarkInstanceFactory(bookmark=bookmark, user=another_user)
        #and should see it in user_bookmarks list
        view_instance = BookmarkList(**{'request':self.request})
        context = view_instance.get_context_data(object_list=view_instance.get_queryset())
        self.assertTrue(bookmark in context['user_bookmarks'])

        
class YourBookmarksPageTests(BookmarkListMixin, BaseBookmarksTests):

    def set_bookmark_and_instance(self, user, site):
        bookmark = BookmarkFactory(adder=user)
        bookmark.sites.add(site)
        instance = BookmarkInstanceFactory(bookmark=bookmark, user=user)
        return {
                'bookmark': bookmark,
                'instance': instance
                }

    def test_list_for_site(self):
        " Only Bookmarks from current site appear on the list "

        bookmarks = {
            'current_site': self.set_bookmark_and_instance(self.user, self.current_site),
            'other_site': self.set_bookmark_and_instance(self.user, SiteFactory())
        }

        self.request.user = self.user

        view_instance = YourBookmarks(**{'request':self.request})
        queryset = view_instance.get_queryset()

        self.assertTrue(bookmarks['current_site']['instance'] in queryset)
        self.assertFalse(bookmarks['other_site']['instance'] in queryset)

    def test_only_users_bookmarks(self):
        "Test only user's bookmarks are displayed"
        bookmarks = {
            'self_user': self.set_bookmark_and_instance(self.user, self.current_site),
            'other_user': self.set_bookmark_and_instance(UserFactory(), self.current_site)
        }

        self.request.user = self.user

        view_instance = YourBookmarks(**{'request':self.request})
        queryset = view_instance.get_queryset()

        self.assertTrue(bookmarks['self_user']['instance'] in queryset)
        self.assertFalse(bookmarks['other_user']['instance'] in queryset)

class UserBookmarksTests(BaseBookmarksTests):

    def setUp(self):
        super(UserBookmarksTests, self).setUp()

        self.client.login(username=self.user.username, password=self.user.raw_password)

    def checkAddBookmark(self, test_url = 'http://google.com/', test_description = 'test bookmark description', user=None):
        ' Check if new "add bookmark" page works. Can be used to check if new bookmark is added or if existing bookmark is saved. '

        all_bookmarks_url = reverse('all_bookmarks')

        url = reverse('add_bookmark')
        response = self.client.post(url, {'url': test_url, 'description' : test_description, 'tags': 'new-tag'}, follow=True)
        self.assertRedirects(response, all_bookmarks_url)
        self.assertContains(response, 'new-tag')

        bookmark_instance = BookmarkInstance.on_site.order_by('-id')[0]
        bookmark = Bookmark.on_site.all().order_by('-id')[0]

        # Check if it is the new bookmark and new instance is created.
        self.assertEquals(bookmark.url, test_url)
        self.assertEquals(bookmark.sites.all()[0].id, 1)
        self.assertEquals(bookmark.sites.all()[0].id, 1)
        self.assertEquals(bookmark_instance.description, test_description)
        self.assertEquals(bookmark_instance.user, user)
        self.assertEquals(bookmark_instance.bookmark, bookmark)

        # Check if the new bookmark has appeared on the page
        response = self.client.get(all_bookmarks_url)
        self.assertContains(response, test_url, 3, 200,)
        self.assertContains(response, test_description, 1, 200,)

        #Try to add existing bookmark.
        response = self.client.post(url, {'url': test_url, 'description' : test_description,}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'bookmark_form', None, 'You have already bookmarked this link.', msg_prefix='')

        self.client.logout()


    # Tests if user can rate bookmarks
    def rateBookmark(self, direction, bookmark=None):
        ' Check if a bookmark can be voted correctly.'
        assert direction in ['up', 'down']

        if bookmark == None:
            bookmark = BookmarkFactory(adder=self.user)
            bookmark.sites.add(self.current_site)

        # Get initial Score value.
        initial = Vote.objects.get_score(bookmark)
        initial_score = int(initial['score'])
        initial_num = int(initial['num_votes'])

        # Vote
        url = reverse('voting.views.vote_on_object', kwargs={'object_id' : bookmark.id, 'direction': direction, }, )
        response = self.client.post(url, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertContains(response, '"success": true',  1, 200)

        # Compare with new score value
        new = Vote.objects.get_score(bookmark)
        new_score = int(new['score'])
        new_num = int(new['num_votes'])
        if direction == 'up':
            self.assertEquals(new_score, initial_score+1)
        else:
            self.assertEquals(new_score, initial_score-1)
        self.assertEquals(new_num, initial_num+1)

        # Check if ajax response contains correct values
        self.assertContains(response, '"score": ' + str(new_score), 1, 200)
        self.assertContains(response, '"num_votes": ' + str(new_num), 1, 200)

        self.client.logout()



    # Tests if user can add new bookmark and rate it.
    def testUserBookmarkNew(self):
        ' Tests if a user can add bookmarks correctly. '

        url = reverse('add_bookmark')
        response = self.client.get(url,)
        self.assertEquals(response.status_code, 200)

        self.checkAddBookmark(user=self.user)

        self.client.logout()


    def testVoteUp(self):

        self.rateBookmark('up')

    def testVoteDown(self):

        self.rateBookmark('down')


    def testSaveBookmark(self):
        ' Tests if user can save bookmark. '

        bookmark = BookmarkFactory(adder=self.user)
        bookmark.sites.add(self.current_site)

        url = reverse('add_bookmark')
        response = self.client.post(url, kwargs={'url':bookmark.url, 'description':bookmark.description})
        self.assertEquals(response.status_code, 200)
        
        self.checkAddBookmark(test_url=bookmark.url, test_description=bookmark.description, user=self.user)

        self.client.logout()

    def testSiteSpecificBookmark(self):
        ' Tests site specific bookmarks. '

        # Deafault SITE_ID=1
        bookmark_site1 = BookmarkFactory(adder=self.user)
        bookmark_site1.sites.add(self.current_site)

        bookmark_site2 = BookmarkFactory(adder=self.user)
        bookmark_site2.sites.add(SiteFactory())

        url = reverse('all_bookmarks')
        response = self.client.get(url)
        self.assertContains(response, bookmark_site1.url)
        self.assertContains(response, bookmark_site1.description)
        self.assertNotContains(response, bookmark_site2.url)
        self.assertNotContains(response, bookmark_site2.description)

        self.assertContains(response, 'tag-site1')
        self.assertNotContains(response, 'tag-site2')

        settings.SITE_ID=2

        response = self.client.get(url)
        self.assertContains(response, bookmark_site2.url)
        self.assertContains(response, bookmark_site2.description)
        self.assertNotContains(response, bookmark_site1.url)
        self.assertNotContains(response, bookmark_site1.description)

        self.assertContains(response, 'tag-site2')
        self.assertNotContains(response, 'tag-site1')

        settings.SITE_ID=1
        self.client.logout()