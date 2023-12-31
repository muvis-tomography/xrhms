# Generated by Django 2.2.13 on 2020-09-08 12:21
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
        ('scans', '0078_archivedrive_scans'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivedrive',
            name='estimated_usage',
            field=models.FloatField(blank=True, default=0, help_text='Estimated disk usage in GB', null=True),
        ),
        migrations.AddField(
            model_name='archivedrive',
            name='no_files',
            field=models.IntegerField(blank=True, default=0, help_text='Number of files on the drive', null=True),
        ),
        migrations.AlterField(
            model_name='archivedrive',
            name='capacity',
            field=models.FloatField(blank=True, help_text='Capacity in GB', null=True),
        ),
    ]
