# Generated by Django 2.2.13 on 2020-09-07 15:33
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
        ('scans', '0074_merge_20200826_1525'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveDrive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('serial_number', models.CharField(blank=True, max_length=40, null=True)),
                ('manufacturer', models.CharField(blank=True, max_length=40, null=True)),
                ('capacity', models.FloatField(blank=True, help_text='Capacity in TB', null=True)),
            ],
        ),
    ]