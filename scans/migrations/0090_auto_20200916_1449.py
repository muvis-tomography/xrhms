# Generated by Django 2.2.13 on 2020-09-16 14:49
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
        ('scans', '0089_auto_20200914_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivedrive',
            name='serial_number',
            field=models.CharField(blank=True, max_length=40, null=True, unique=True),
        ),
    ]
