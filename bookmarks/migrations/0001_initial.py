# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=511)),
                ('description', models.TextField(verbose_name='description')),
                ('note', models.TextField(verbose_name='note', blank=True)),
                ('has_favicon', models.BooleanField(default=False, verbose_name='has favicon')),
                ('favicon_checked', models.DateTimeField(default=datetime.datetime.now, verbose_name='favicon checked')),
                ('added', models.DateTimeField(default=datetime.datetime.now, verbose_name='added')),
                ('adder', models.ForeignKey(related_name='added_bookmarks', verbose_name='adder', to=settings.AUTH_USER_MODEL)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
                'ordering': ('-added',),
            },
        ),
        migrations.CreateModel(
            name='BookmarkInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('saved', models.DateTimeField(default=datetime.datetime.now, verbose_name='saved')),
                ('description', models.TextField(verbose_name='description')),
                ('note', models.TextField(verbose_name='note', blank=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('bookmark', models.ForeignKey(related_name='saved_instances', verbose_name='bookmark', to='bookmarks.Bookmark')),
                ('user', models.ForeignKey(related_name='saved_bookmarks', verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
