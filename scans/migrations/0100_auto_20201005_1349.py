# Generated by Django 2.2.13 on 2020-10-05 13:49
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
        ('scans', '0099_auto_20200930_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='omeplane',
            name='binning',
        ),
        migrations.AddField(
            model_name='omechannel',
            name='binning',
            field=models.CharField(blank=True, help_text='Was the detector binned for acquisition', max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='omechannel',
            name='detector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scans.OmeDetector'),
        ),
    ]