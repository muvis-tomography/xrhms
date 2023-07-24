# Generated by Django 2.2.13 on 2020-06-10 12:42
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
        ('scans', '0063_auto_20200610_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='scan',
            name='tname',
            field=models.CharField(db_index=True, default='NULL_NAME', max_length=255),
            preserve_default=False,
        ),
        migrations.RunSQL("UPDATE scans_scan AS t1 INNER JOIN scans_nikonctscan AS t2 on t1.id = t2.scan_ptr_id SET t1.tname = t2.name"),
        migrations.RunSQL("UPDATE scans_scan AS t1 INNER JOIN scans_dectrisctscan AS t2 on t1.id = t2.scan_ptr_id SET t1.tname = t2.name"),
        migrations.RemoveField(
            model_name='nikonctscan',
            name='name',
        ),
        migrations.RenameField(
            model_name='scan',
            old_name='tname',
            new_name='name'
        ),
    ]
