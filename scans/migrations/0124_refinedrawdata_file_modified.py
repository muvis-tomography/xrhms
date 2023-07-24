# Generated by Django 2.2.17 on 2021-01-12 11:13
"""
    Copyright 2023 University of Southampton
    Dr Philip Basford
    μ-VIS X-Ray Imaging Centre

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0123_merge_20210112_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='refinedrawdata',
            name='file_modified',
            field=models.DateTimeField(blank=True, help_text='When the file was last modified', null=True),
        ),
    ]