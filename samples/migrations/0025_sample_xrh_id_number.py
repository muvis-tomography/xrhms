# Generated by Django 2.2.7 on 2019-11-07 10:06
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
        ('samples', '0024_auto_20191106_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='xrh_id_number',
            field=models.IntegerField(blank=True, db_index=True, default=0, editable=False, help_text='The numeric part of the ID without the checksum', verbose_name='XRH ID Number'),
            preserve_default=False,
        ),
    ]
