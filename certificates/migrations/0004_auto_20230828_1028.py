# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-08-28 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0003_auto_20230828_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificatetemplate',
            name='template_html',
            field=models.TextField(blank=True, null=True),
        ),
    ]
