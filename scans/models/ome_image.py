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
from django.urls import reverse
from django.utils.html import mark_safe
from private_storage.fields import PrivateFileField

class OmeImage(models.Model):

    class Meta:
        verbose_name = "OME Image"
        verbose_name_plural = "OME Images"
    def get_subfolder(self):
        return [self.scan_id, self.pk]

    scan = models.ForeignKey(
        "OmeData",
        on_delete=models.CASCADE,
        blank=False,
        null=False)
    image_id = models.CharField(
        verbose_name="Image ID",
        max_length=20,
        blank=True,
        null=True)
    filename = models.CharField(
        max_length=255,
        blank=False,
        null=False)
    name = models.CharField(
        max_length=80,
        blank=True,
        null=True)
    objective = models.ForeignKey(
        "OmeObjective",
        on_delete=models.PROTECT,
        blank=True,
        null=True)
    pixels_big_endian = models.BooleanField(
        blank=True,
        null=True)
    pixels_dimension_order = models.CharField(
        max_length=12,
        blank=True,
        null=True)
    pixels_interleaved = models.BooleanField(
        blank=True,
        null=True)
    pixels_significant_bits = models.IntegerField(
        blank=True,
        null=True)
    pixels_type = models.CharField(
        max_length=10,
        blank=True,
        null=True)
    physical_size_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Physical size X",
        help_text="X dimension in µm")
    physical_size_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Physical size Y",
        help_text="Y dimension in µm")
    pixels_x = models.IntegerField(
        blank=True,
        verbose_name="Pixels X",
        null=True)
    pixels_y = models.IntegerField(
        blank=True,
        verbose_name="Pixels Y",
        null=True)
    size_c = models.IntegerField(
        blank=True,
        verbose_name="Size C",
        null=True)
    size_z = models.IntegerField(
        blank=True,
        verbose_name="Size Z",
        null=True)
    size_t = models.IntegerField(
        blank=True,
        verbose_name="Size T",
        null=True)
    refractive_index = models.FloatField(
        blank=True,
        null=True)
    preview = PrivateFileField(
        "Preview",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    scan_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Time taken to scan this image (s)")

    def objective_model(self):
        url =  reverse('admin:scans_omeobjective_change', args=[self.objective_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.objective.model))
    objective_model.short_description = "Objective model"

    def objective_nominal_magnification(self):
        return "{}x".format(self.objective.nominal_magnification) #pylint: disable=no-member
    objective_nominal_magnification.short_description = "Objective nominal magnification"

    def scan_time_readable(self):
        return timedelta(seconds=self.scan_time)
    scan_time_readable.short_description = "Scan time"

    def __str__(self):
        return "Image ({})".format(self.pk)
