# Generated by Django 2.2.20 on 2021-06-03 14:38
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
        ('scans', '0138_auto_20210524_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='nikonctscan',
            name='veiling_glare_applied',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
