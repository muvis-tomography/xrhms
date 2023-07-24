# Generated by Django 2.2.17 on 2021-03-04 16:35
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
        ('scans', '0131_merge_20210223_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refinedrawdata',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scans.Scan'),
        ),
        migrations.AlterField(
            model_name='scan',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='The scan object that this one is derived from', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='scans.Scan'),
        ),
        migrations.AlterField(
            model_name='scanattachment',
            name='attachment_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scans.ScanAttachmentType'),
        ),
        migrations.AlterField(
            model_name='scanattachment',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scans.Scan'),
        ),
        migrations.AlterField(
            model_name='scanattachmenttypesuffix',
            name='attachment_type',
            field=models.ForeignKey(help_text='The attachment type this relates to', on_delete=django.db.models.deletion.PROTECT, to='scans.ScanAttachmentType'),
        ),
        migrations.AlterField(
            model_name='scannerscreenshot',
            name='scanner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scans.Machine', verbose_name='Scanner'),
        ),
    ]
