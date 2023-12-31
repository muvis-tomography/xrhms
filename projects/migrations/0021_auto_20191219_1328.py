# Generated by Django 2.2.7 on 2019-12-19 13:28
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
        ('projects', '0020_project_full_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='funder',
            options={'verbose_name': 'Funding source ', 'verbose_name_plural': 'Funding sources'},
        ),
        migrations.AddField(
            model_name='project',
            name='mta_approved',
            field=models.BooleanField(blank=True, help_text='Has the MTA paperwork for this project been approved?', null=True, verbose_name='MTA received'),
        ),
        migrations.AddField(
            model_name='project',
            name='mta_needed',
            field=models.BooleanField(default=False, help_text='Does this project need a Material Transfer Agreement (MTA)?', verbose_name='Material trasfer agreement needed'),
        ),
        migrations.AddField(
            model_name='project',
            name='mta_reference',
            field=models.TextField(blank=True, help_text='Any reference details for the MTA', null=True),
        ),
        migrations.AlterField(
            model_name='funder',
            name='name',
            field=models.CharField(db_index=True, help_text='Name of the Funding source', max_length=200, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='funder',
            name='url',
            field=models.URLField(blank=True, help_text='Link to the Funding source website', verbose_name='Website'),
        ),
        migrations.AlterField(
            model_name='project',
            name='collaboration_agreement',
            field=models.BooleanField(default=False, help_text='Has a signed memorandum of understanding been received?', verbose_name='Memorandum of Understanding'),
        ),
        migrations.AlterField(
            model_name='project',
            name='ethics_reference',
            field=models.TextField(blank=True, help_text='Any reference details for the ethics approval', null=True),
        ),
    ]
