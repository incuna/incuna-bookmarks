# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='added'),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='favicon_checked',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='favicon checked'),
        ),
        migrations.AlterField(
            model_name='bookmarkinstance',
            name='saved',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='saved'),
        ),
    ]
