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
from datetime import timedelta
from django.db import models
from django.conf import settings

from private_storage.fields import PrivateFileField

from .scan import Scan

class OmeData(Scan):
    class Meta:
        verbose_name = "Histology Slide"
        verbose_name_plural = "Histology Slides"
    def get_subfolder(self):
        return [self.pk]

    overview = PrivateFileField(
        "Overview",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    staining_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional information about the staining protocol used")
    staining = models.ForeignKey(
        "Staining",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Details of the standard staining protocol used if any")
    scan_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Total scan time for all images (s)")

    def scan_time_readable(self):
        return timedelta(seconds=self.scan_time)
    scan_time_readable.short_description = "Scan time"
