from unittest import expectedFailure

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.conf import settings

from bookmarks.models import Bookmark, BookmarkInstance
from voting.models import Vote



class UserBookmarksTests(TestCase):
    # FIXME: update the fixtures so they load, or replace with setUp method
    # fixtures = ['accountdata.json', 'bookmarks.json', 'sites.json']

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

        user = User.objects.get(username='testuser')
        self.client.login(username=user.username, password='test')

        if bookmark == None:
            bookmark = Bookmark.on_site.all()[0]

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
    @expectedFailure
    def testUserBookmarkNew(self):
        ' Tests if a user can add bookmarks correctly. '
        user = User.objects.get(username='testuser')
        self.client.login(username=user.username, password='test')

        url = reverse('add_bookmark')
        response = self.client.get(url,)
        self.assertEquals(response.status_code, 200)

        self.checkAddBookmark(user=user)

        self.client.logout()


    @expectedFailure
    def testVoteUp(self):

        self.rateBookmark('up')

    @expectedFailure
    def testVoteDown(self):

        self.rateBookmark('down')


    @expectedFailure
    def testSaveBookmark(self):
        ' Tests if user can save bookmark. '
        user = User.objects.get(username='testuser')
        self.client.login(username=user.username, password='test')

        bookmark = Bookmark.objects.all()[1]

        url = reverse('add_bookmark')
        response = self.client.post(url, kwargs={'url':bookmark.url, 'description':bookmark.description})
        self.assertEquals(response.status_code, 200)

        self.checkAddBookmark(test_url=bookmark.url, test_description=bookmark.description, user=user)

        self.client.logout()

    @expectedFailure
    def testSiteSpecificBookmark(self):
        ' Tests site specific bookmarks. '
        user = User.objects.get(username='testuser')
        self.client.login(username=user.username, password='test')

        # Deafault SITE_ID=1
        bookmarks = Bookmark.objects.all()
        bookmark_site1 = bookmarks.get(id=1)
        bookmark_site2 = bookmarks.get(id=2)

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
