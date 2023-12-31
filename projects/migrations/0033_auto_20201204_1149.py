# Generated by Django 2.2.13 on 2020-12-04 11:49
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
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0032_project_watch_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='watch_list',
            field=models.ManyToManyField(blank=True, help_text='Users to email whenever there is a project update', related_name='watching', to=settings.AUTH_USER_MODEL),
        ),
    ]
