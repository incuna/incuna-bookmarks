import factory
from django.contrib.auth.models import User

from ..models import Bookmark, BookmarkInstance


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence('user-{}'.format)

    class Meta:
        model = User


class BookmarkFactory(factory.DjangoModelFactory):
    adder = factory.SubFactory(UserFactory)

    class Meta:
        model = Bookmark


class BookmarkInstanceFactory(factory.DjangoModelFactory):
    bookmark = factory.SubFactory(BookmarkFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BookmarkInstance
