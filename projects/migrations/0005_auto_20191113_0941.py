# Generated by Django 2.2.7 on 2019-11-13 09:41
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
        ('projects', '0004_project_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Name of the Organisation', max_length=200, unique=True, verbose_name='Name')),
                ('url', models.URLField(blank=True, help_text='Link to the organisation website', verbose_name='Project website')),
                ('notes', models.TextField(blank='True', help_text='Additional notes')),
            ],
        ),
        migrations.AddField(
            model_name='contact',
            name='affiliation',
            field=models.ManyToManyField(blank=True, help_text='Linked Organisations', to='projects.Institution'),
        ),
        migrations.AddField(
            model_name='project',
            name='affiliation',
            field=models.ManyToManyField(blank=True, help_text='Linked Organisations', to='projects.Institution'),
        ),
    ]
