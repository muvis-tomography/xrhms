# Generated by Django 2.2.13 on 2020-10-08 13:46
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
        ('scans', '0105_auto_20201008_1343'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='omechannel',
            options={'verbose_name': 'OME Channel', 'verbose_name_plural': 'OME Channels'},
        ),
        migrations.AlterModelOptions(
            name='omedetector',
            options={'verbose_name': 'OME Detector', 'verbose_name_plural': 'OME Detectors'},
        ),
        migrations.AlterModelOptions(
            name='omeplane',
            options={'verbose_name': 'OME Plane', 'verbose_name_plural': 'OME Planes'},
        ),
        migrations.AlterField(
            model_name='omechannel',
            name='channel_id',
            field=models.CharField(help_text='Channel ID', max_length=40, verbose_name='OME Channel'),
        ),
    ]
