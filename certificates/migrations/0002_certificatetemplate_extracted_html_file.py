# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-07-31 07:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificatetemplate',
            name='extracted_html_file',
            field=models.FileField(blank=True, null=True, upload_to=b''),
        ),
    ]
