# Generated by Django 2.2.13 on 2020-09-14 15:40
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
        ('scans', '0088_auto_20200914_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanarchive',
            name='file_count',
            field=models.IntegerField(blank=True, help_text='The number of files in this folder and subtree', null=True),
        ),
        migrations.AddField(
            model_name='scanarchive',
            name='total_size',
            field=models.FloatField(blank=True, help_text='The size of the folder and subtree on the disk (GiB)', null=True),
        ),
    ]
