from haystack.indexes import CharField, DateTimeField, RealTimeSearchIndex, Indexable

from models import Bookmark


class BookmarkIndex(RealTimeSearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='description')
    author = CharField(model_attr='adder')
    pub_date = DateTimeField(model_attr='added')
    summary = CharField(model_attr='note')
    sites = CharField(model_attr='site_slugs')

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_model(self):
        return Bookmark
