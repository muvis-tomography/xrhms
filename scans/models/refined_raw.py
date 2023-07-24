#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use
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

from pathlib import Path

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.urls import reverse

class RefinedRawExtension(models.Model):
    extension = models.CharField(
        max_length=10,
        unique=True,
        blank=False,
        null=False,
        help_text="Extension to search for")
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about the file extension")

    def __str__(self):
        return self.extension

class RefinedRawData(models.Model):
    class Meta:
        verbose_name_plural = "Refined Raw Data"
    scan = models.ForeignKey(
        "Scan",
        on_delete=models.PROTECT,
        null=False,
        blank=False)
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Name of the refined file")
    path = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Relative path for the file based on scan data dir")
    scan = models.ForeignKey(
        "Scan",
        on_delete=models.PROTECT,
        null=False,
        blank=False)
    first_indexed = models.DateTimeField(
        auto_now_add=True,
        help_text="When the system first discovered the file")
    checksum = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        null=True,
        help_text="Checksum for automatically ingested files")
    last_updated = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was last updated")
    shareable = models.BooleanField(
        default=True,
        null=False,
        blank=False,
        help_text="Can this file be shared publically")
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about the file extension")
    file_available = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        help_text="Is the file currently on the datastore")
    file_modified = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the file was last modified")

    def __str__(self):
        return "{} {}".format(str(self.scan), self.name)

    def name_link(self):
        url = reverse('admin:scans_refinedrawdata_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.name))
    name_link.short_description = "Name"

    def scan_link(self):
        url = reverse('admin:scans_scan_change', args=[self.scan_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.scan))
    scan_link.short_description = "Scan"
    scan_link.admin_order_field = "Scan"

    def check_exists(self):
        path = Path(self.scan.full_path().parent, self.path, self.name) #pylint: disable=no-member
        return path.exists()

    def update_exists(self):
        new_status = self.check_exists()
        change =  new_status != self.file_available
        if change:
            self.file_available = new_status
            self.last_updated = timezone.now()
            self.save()
        return (new_status, change)
