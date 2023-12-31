# Generated by Django 2.2.13 on 2020-12-14 13:15
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
from samples.models import SampleReport
from django.contrib.auth import get_user_model

class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0084_samplereport_generated_by'),
    ]
    def assign_user_to_report(apps, schema_editor):
        user = get_user_model().objects.get(pk=1)
        reports = SampleReport.objects.all()
        for report in reports:
            if not report.all_videos_excluded():
                report.generated_by = user
                report.save()

    operations = [
        migrations.RunPython(assign_user_to_report)
    ]
