# Generated by Django 2.2.10 on 2020-03-02 15:40
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
        ('samples', '0047_auto_20200224_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleAttachmentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Name for the attachment type', max_length=255, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of the attachment type', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SampleAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Short name for the attachment', max_length=255, null=True)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Notes about the attachment', null=True)),
                ('attachment', private_storage.fields.PrivateFileField(storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to='sample', verbose_name='Attachment')),
                ('attachment_type', models.ForeignKey(blank=True, help_text='The type of the attachment', null=True, on_delete='models.PROTECT', to='samples.SampleAttachmentType')),
                ('sample', models.ForeignKey(on_delete='models.PROTECT', to='samples.Sample')),
            ],
        ),
    ]
