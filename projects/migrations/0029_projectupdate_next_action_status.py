# Generated by Django 2.2.13 on 2020-12-02 15:50
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

from projects.models import ProjectUpdate, TASK_COMPLETE
class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_auto_20200908_1458'),
    ]

    def update_status(apps, schema_editor):
        for update in ProjectUpdate.objects.all():
            if update.next_action_complete:
                update.next_action_status = TASK_COMPLETE
                update.save()

    operations = [
        migrations.AddField(
            model_name='projectupdate',
            name='next_action_status',
            field=models.CharField(choices=[('CO', 'Complete'), ('PE', 'Pending'), ('WD', "Won't Complete")], default='PE', max_length=2),
        ),
        migrations.RunPython(update_status),
    ]
