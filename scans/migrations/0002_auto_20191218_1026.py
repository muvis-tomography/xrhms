# Generated by Django 2.2.7 on 2019-12-18 10:26
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
from scans.models import Server, Share

class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0001_initial'),
    ]

    def insertData(apps, schema_editor):
        medxdata1 = Server(
            host_name="medxdata1",
            internal_name="medxdata1.internal.xrayhistology.org",
            internal_ipv4_address="192.168.17.39",
            external_name="medxdata1.soton.ac.uk",
            external_ipv4_address="152.78.4.25")
        medxdata1.save()
        xrh_data1 = Server(
            host_name="xrh-data1",
            internal_name="xrh-data1.internal.xrayhistology.org",
            internal_ipv4_address="192.168.19.131",
            external_name="xrh-server.clients.soton.ac.uk",
            external_ipv4_address="152.78.4.35")
        xrh_data1.save()
        medxdata_a = Share(
            name="DataA",
            server=medxdata1,
            linux_mnt_point="/mnt/medxdataA/",
            windows_mnt_point="Z:")
        medxdata_a.save()
        medxdata_b = Share(
            name="DataB",
            server=medxdata1,
            linux_mnt_point="/mnt/medxdataB/",
            windows_mnt_point="Y:")
        medxdata_b.save()
        xrh_warm = Share(
            name="Warm",
            server=xrh_data1,
            linux_mnt_point="/mnt/xrh-warm",
            windows_mnt_point="I:")
        xrh_warm.save()
        xrh_hot = Share(
            name="Hot",
            server=xrh_data1,
            linux_mnt_point="/mnt/xrh-hot",
            windows_mnt_point="H:")
        xrh_hot.save()

    operations = [
        migrations.RunPython(insertData)
    ]
