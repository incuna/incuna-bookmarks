from django import forms
from django.utils.translation import ugettext_lazy as _

from tagging.forms import TagField

from bookmarks.models import BookmarkInstance


class BookmarkInstanceForm(forms.ModelForm):
    url = forms.URLField(
        label="URL",
        widget=forms.TextInput(attrs={"size": 40}),
    )
    description = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"size": 40}),
    )
    redirect = forms.BooleanField(label="Redirect", required=False)
    tags = TagField(label="Tags", required=False)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(BookmarkInstanceForm, self).__init__(*args, **kwargs)
        # hack to order fields
        self.fields.keyOrder = ['url', 'description', 'note', 'tags', 'redirect']

    def clean(self):
        if 'url' not in self.cleaned_data:
            return
        bookmarks = BookmarkInstance.on_site.filter(
            bookmark__url=self.cleaned_data['url'],
            user=self.user,
        )
        if bookmarks.count() > 0:
            raise forms.ValidationError(
                _("You have already bookmarked this link."),
            )
        return self.cleaned_data

    def should_redirect(self):
        if self.cleaned_data["redirect"]:
            return True
        else:
            return False

    def save(self, commit=True):
        url = self.cleaned_data['url']
        self.instance.bookmark = self.instance.get_or_create_bookmark(url)
        return super(BookmarkInstanceForm, self).save(commit)

    class Meta:
        model = BookmarkInstance
        fields = (
            'bookmark',
            'user',
            'saved',
            'description',
            'note',
            'tags',
            'url',
            'redirect',
        )
