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
from django.db import models

class OmeDetector(models.Model):
    class Meta:
        verbose_name = "OME Detector"
        verbose_name_plural = "OME Detectors"

    manufacturer = models.CharField(
        max_length=100,
        db_index=True,
        blank=False,
        null=False)
    model = models.CharField(
        max_length=50,
        db_index=True,
        blank=False,
        null=False)
    serial_number = models.CharField(
        max_length=50,
        db_index=True,
        blank=True,
        null=True)
    detector_type = models.CharField(
        max_length=30,
        blank=True,
        null=True)
    gain = models.FloatField(
        blank=True,
        null=True)

    def __str__(self):
        return "{} {} ({})".format(self.manufacturer, self.model, self.serial_number)
