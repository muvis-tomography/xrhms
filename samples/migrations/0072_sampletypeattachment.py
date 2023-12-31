# Generated by Django 2.2.11 on 2020-05-07 10:15
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
import private_storage.fields
import private_storage.storage.files


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0071_auto_20200507_0925'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleTypeAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Short name for the attachment', max_length=255)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Notes about the attachment', null=True)),
                ('attachment', private_storage.fields.PrivateFileField(storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to='sample_type', verbose_name='Attachment')),
                ('sample_type', models.ForeignKey(on_delete='models.PROTECT', to='samples.SampleType')),
            ],
        ),
    ]
