# Generated by Django 2.2.7 on 2019-12-02 15:06
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
        ('muvis', '0002_auto_20191202_1448'),
    ]

    operations = [
        migrations.CreateModel(
            name='MuvisBug',
            fields=[
                ('muvis_id', models.IntegerField(help_text='Muvis bug ID', primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, editable=False, help_text='Muvis bug title', max_length=255)),
                ('status', models.ForeignKey(help_text='Status of muvis bug', on_delete=django.db.models.deletion.PROTECT, to='muvis.BugzillaStatus')),
            ],
        ),
    ]
