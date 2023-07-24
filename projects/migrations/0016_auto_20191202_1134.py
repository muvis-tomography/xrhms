# Generated by Django 2.2.7 on 2019-12-02 11:34
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
        ('projects', '0015_projectupdate_next_action_complete_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='ethics_approved',
            field=models.BooleanField(blank=True, help_text='Has the ethics paperwork for this project been approved?', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='ethics_needed',
            field=models.BooleanField(default=False, help_text='Does this project need ethics approval?'),
        ),
        migrations.AddField(
            model_name='project',
            name='ethics_reference',
            field=models.TextField(blank=True, help_text='Any reference details for the ehtics approval', null=True),
        ),
    ]
