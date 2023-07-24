# Generated by Django 2.2.7 on 2019-11-13 11:30
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
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0007_auto_20191113_1033'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Name of status', max_length=50, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of status')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Last Updated')),
                ('last_action_date', models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='Last Action (Date)')),
                ('last_action', models.TextField(blank=True, null=True, verbose_name='Details of Last Action')),
                ('notes', models.TextField(blank=True, null=True)),
                ('next_action', models.TextField(blank=True, null=True)),
                ('next_action_deadline', models.DateField(blank=True, db_index=True, null=True)),
                ('project', models.ForeignKey(help_text='Project the update relates to', on_delete=django.db.models.deletion.PROTECT, to='projects.Project')),
                ('status', models.ForeignKey(blank=True, help_text='Current status of the project', on_delete=django.db.models.deletion.PROTECT, to='projects.ProjectStatus')),
                ('user', models.ForeignKey(blank=True, help_text='The user who made the change', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='By')),
            ],
        ),
    ]
