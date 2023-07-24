# Generated by Django 2.2.11 on 2020-04-29 14:09
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
from django.db import migrations
from scans.models import ScanAttachmentType


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0042_auto_20200429_1349'),
    ]
    def insert_attachment_types(apps, schema_editor):
        types = [
            ("Raw radiograph video", "A video of the raw radiographs from the scan"),
        ]

        for i in types:
            if ScanAttachmentType.objects.filter(name=i[0]).count() == 0:
                t = ScanAttachmentType(name=i[0], description=i[1])
                t.save()

    operations = [
         migrations.RunPython(insert_attachment_types),
    ]