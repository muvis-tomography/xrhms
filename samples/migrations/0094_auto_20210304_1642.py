# Generated by Django 2.2.17 on 2021-03-04 16:42
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
        ('samples', '0093_auto_20210304_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportscanmapping',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='samples.SampleReport'),
        ),
        migrations.AlterField(
            model_name='reportscanmapping',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scans.Scan'),
        ),
    ]
