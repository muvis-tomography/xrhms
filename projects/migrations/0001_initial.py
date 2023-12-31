# Generated by Django 2.2.6 on 2019-10-28 11:21
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
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Name')),
                ('email', models.EmailField(blank=True, max_length=200, verbose_name='Email address')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='Phone Number')),
                ('address', models.TextField(blank=True, verbose_name='Postal address')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Project Name')),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(blank=True, verbose_name='Project website')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_contact', to='projects.Contact', verbose_name='Primary Contact')),
                ('other_contacts', models.ManyToManyField(blank=True, related_name='project_contact_list', to='projects.Contact', verbose_name='Other Contacts')),
                ('pi', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_pi', to='projects.Contact', verbose_name='Principal Investigator')),
            ],
        ),
    ]
