# Generated by Django 2.2.17 on 2021-01-11 16:32
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
        ('scans', '0120_auto_20201214_1712'),
    ]

    operations = [
        migrations.CreateModel(
            name='RefinedRawExtension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extension', models.CharField(help_text='Extension to search for', max_length=10, unique=True)),
                ('notes', models.TextField(blank=True, help_text='Notes about the file extension', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RefinedRawData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the refined file', max_length=255)),
                ('path', models.CharField(help_text='Relative path for the file based on scan data dir', max_length=255)),
                ('first_indexed', models.DateTimeField(auto_now_add=True)),
                ('checksum', models.CharField(blank=True, db_index=True, help_text='Checksum for automatically ingested files', max_length=64, null=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
                ('sharable', models.BooleanField(default=True, help_text='Can this file be shared publically')),
                ('notes', models.TextField(blank=True, help_text='Notes about the file extension', null=True)),
                ('file_available', models.BooleanField(default=True, help_text='Is the file currently on the datastore')),
                ('scan', models.ForeignKey(on_delete='models.PROTECT', to='scans.Scan')),
            ],
            options={
                'verbose_name_plural': 'Refined Raw Data',
            },
        ),
    ]
