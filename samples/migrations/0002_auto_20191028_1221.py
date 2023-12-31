# Generated by Django 2.2.6 on 2019-10-28 12:21
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
        ('samples', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='diseasestatus',
            options={'verbose_name_plural': 'Disease Statuses'},
        ),
        migrations.AlterModelOptions(
            name='species',
            options={'verbose_name_plural': 'Species'},
        ),
        migrations.AlterModelOptions(
            name='tissue',
            options={'verbose_name_plural': 'Tissue'},
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='The unique name/id for the sample', max_length=50, unique=True)),
                ('description', models.TextField(blank=True, help_text='Long form description of the sample')),
                ('date_entered', models.DateTimeField(auto_now_add=True)),
                ('disease_status', models.ForeignKey(blank=True, help_text='Any known details about the disease status of the sample', on_delete=django.db.models.deletion.PROTECT, to='samples.DiseaseStatus')),
                ('sample_type', models.ForeignKey(help_text='The type of the sample', on_delete=django.db.models.deletion.PROTECT, to='samples.SampleType', verbose_name='Type')),
                ('species', models.ForeignKey(help_text='What species is the sample from', on_delete=django.db.models.deletion.PROTECT, to='samples.Species')),
                ('storage_requirement', models.ForeignKey(help_text='Any spefic requirements about how the item is stored', on_delete=django.db.models.deletion.PROTECT, to='samples.StorageRequirement')),
                ('tissue', models.ForeignKey(help_text='The tissue that the sample is of', on_delete=django.db.models.deletion.PROTECT, to='samples.Tissue')),
            ],
        ),
    ]
