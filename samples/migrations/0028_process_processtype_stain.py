# Generated by Django 2.2.7 on 2019-11-07 17:58
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
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('samples', '0027_auto_20191107_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the process', max_length=200, unique=True)),
                ('description', models.TextField(blank=True, help_text='A description of the process')),
            ],
        ),
        migrations.CreateModel(
            name='Stain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the stain', max_length=200, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of the Chemical')),
            ],
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(db_index=True, default=datetime.datetime(2019, 11, 7, 17, 58, 52, 882157, tzinfo=utc), help_text='When was the process carried out')),
                ('start_slice', models.IntegerField(blank=True, help_text='The number of the first slice created', null=True)),
                ('number_of_slices', models.IntegerField(blank=True, help_text='The number of slices created', null=True)),
                ('process', models.ForeignKey(help_text='The process carried out on the sample', on_delete=django.db.models.deletion.PROTECT, to='samples.ProcessType')),
                ('sample', models.ForeignKey(help_text='The sample that was used in the process', on_delete=django.db.models.deletion.PROTECT, to='samples.Sample')),
                ('stain_used', models.ForeignKey(blank=True, help_text='The Stain used as part of the process', null=True, on_delete=django.db.models.deletion.PROTECT, to='samples.Stain')),
                ('user', models.ForeignKey(help_text='The user who carried out the process', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
