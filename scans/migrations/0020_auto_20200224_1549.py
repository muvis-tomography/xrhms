# Generated by Django 2.2.10 on 2020-02-24 15:49
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
        ('scans', '0019_auto_20200224_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nikonctscan',
            name='xray_kv',
            field=models.IntegerField(blank=True, null=True, verbose_name='X-Ray Voltage (kV)'),
        ),
        migrations.AlterField(
            model_name='nikonctscan',
            name='xray_ua',
            field=models.IntegerField(blank=True, null=True, verbose_name='X-Ray Current (µA)'),
        ),
    ]
