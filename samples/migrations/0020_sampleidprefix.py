# Generated by Django 2.2.7 on 2019-11-04 15:27
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
        ('samples', '0019_samplelocationmapping_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleIdPrefix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(db_index=True, help_text='The characters that are available for use as sample prefixes', max_length=4, unique=True)),
                ('description', models.TextField(blank=True, help_text='What the short code is used for')),
            ],
        ),
    ]
