# Generated by Django 2.2.17 on 2021-02-22 13:45
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
from scans.models import Scan

class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0127_scan_parent'),
    ]

    def find_parents(apps, schema_editor):
        scans = Scan.objects.all()
        for scan in scans:
            scan.find_parent()

    operations = [
        migrations.RunPython(find_parents)
    ]