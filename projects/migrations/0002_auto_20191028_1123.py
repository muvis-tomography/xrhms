# Generated by Django 2.2.6 on 2019-10-28 11:23
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

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='address',
            field=models.TextField(blank=True, help_text='Address to send samples to', verbose_name='Postal address'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, help_text='Email address used to contact the person', max_length=200, verbose_name='Email address'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(db_index=True, help_text='Name of the person', max_length=200, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(blank=True, help_text='Contact phone number to use', max_length=30, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='project',
            name='contact',
            field=models.ForeignKey(help_text='The main contact for the project (may be the PI)', on_delete=django.db.models.deletion.PROTECT, related_name='project_contact', to='projects.Contact', verbose_name='Primary Contact'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, help_text='A longer form description of the project'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(db_index=True, help_text='A Short(ish) name for the project', max_length=255, unique=True, verbose_name='Project Name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='other_contacts',
            field=models.ManyToManyField(blank=True, help_text='Other contacts for the project', related_name='project_contact_list', to='projects.Contact', verbose_name='Other Contacts'),
        ),
        migrations.AlterField(
            model_name='project',
            name='pi',
            field=models.ForeignKey(help_text='The principle investigator on the project', on_delete=django.db.models.deletion.PROTECT, related_name='project_pi', to='projects.Contact', verbose_name='Principal Investigator'),
        ),
        migrations.AlterField(
            model_name='project',
            name='url',
            field=models.URLField(blank=True, help_text='Link to the project website', verbose_name='Project website'),
        ),
    ]
