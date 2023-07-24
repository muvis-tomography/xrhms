# Generated by Django 2.2.6 on 2019-10-28 13:29
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
        ('projects', '0002_auto_20191028_1123'),
        ('samples', '0004_auto_20191028_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='project',
            field=models.ManyToManyField(help_text='Projects to which this sample is associated', to='projects.Project'),
        ),
    ]
