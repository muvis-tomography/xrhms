# Generated by Django 2.2.7 on 2019-12-04 11:43
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
        ('muvis', '0003_muvisbug'),
    ]

    operations = [
        migrations.CreateModel(
            name='BugzillaResolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Description of how a bug was resolved', max_length=20, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='muvisbug',
            name='resolution',
            field=models.ForeignKey(blank=True, help_text='How the ticket was resolved', null=True, on_delete=django.db.models.deletion.PROTECT, to='muvis.BugzillaResolution'),
        ),
    ]
