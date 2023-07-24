#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use, too-many-lines
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
import csv
from datetime import timedelta
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
# Create your views here.

def scan_comparison_csv(queryset):
    data = compare_scans(queryset)
    response = HttpResponse(content_type="text\\csv")
    response['Content-Disposition'] = 'attachment; filename="scans.csv"'
    csv_writer = csv.writer(response)
    for line in data:
        csv_writer.writerow(line)
    return response


def compare_scans(queryset):
    params = [
        ("xray_kv", "Energy (kVp)"),
        ("power", "Power (W)"),
        ("xray_head", "X-ray Head"),
        ("estimate_time", "Estimated scan time"),
        ("projections", "Projections"),
        ("frames_per_projection", "Frames per projection"),
        ("voxel_size_x", "X Voxel size (mm)"),
        ("geometric_magnification", "Geometric Magnification"),
#            ("", "ImZ (mm)",
        ("src_to_detector", "Source to detector (mm)"),
        ("shuttling", "Shuttling"),
    ]
    data = []
    data.append([""])
    for scan in queryset:
        data[0].append(str(scan))
    for (param, label) in params:
        line = [label]
        for scan in queryset:
            if not hasattr(scan, param):
                line.append(None)
                continue
            attr = getattr(scan, param)
            if callable(attr):
                line.append(str(attr()))
            else:
                line.append(str(attr))
        data.append(line)
    return data

def transfer_time_table(request, queryset, context):
    data = calculate_transfer_times(queryset)
    context["scans"] =  data
    return render(request, "admin/scans/transfer_times.html", context=context)

def calculate_transfer_times(queryset):
    total_size = 0
    dataset = []
    for scan in queryset:
        scan_data = [scan.name]
        disk_usage = float(scan.disk_usage())
        total_size += disk_usage
        scan_data.append(round(disk_usage / (1024 * 1024 * 1024), 3))
        scan_data.append(timedelta(seconds=round(disk_usage / settings.TRANSFER_SPEED_1GBIT, 0)))
        scan_data.append(timedelta(seconds=round(disk_usage / settings.TRANSFER_SPEED_USB2, 0)))
        scan_data.append(timedelta(seconds=round(disk_usage / settings.TRANSFER_SPEED_USB3, 0)))
        dataset.append(scan_data)
    total_line = ["TOTAL", round(total_size / (1024 * 1024 * 1024), 3)]
    total_line.append(timedelta(seconds=round(total_size / settings.TRANSFER_SPEED_1GBIT, 0)))
    total_line.append(timedelta(seconds=round(total_size / settings.TRANSFER_SPEED_USB2, 0)))
    total_line.append(timedelta(seconds=round(total_size / settings.TRANSFER_SPEED_USB3, 0)))
    dataset.append(total_line)
    return dataset
