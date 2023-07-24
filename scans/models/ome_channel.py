#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use
from django.db import models
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
class OmeChannel(models.Model):
    class Meta:
        verbose_name = "OME Channel"
        verbose_name_plural = "OME Channels"
    name = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        help_text="Name of the channel")
    channel_id = models.CharField(
        max_length=40,
        blank=False,
        null=False,
        verbose_name="OME Channel",
        help_text="Channel ID")
    emission_wavelength = models.FloatField(
        blank=True,
        null=True,
        help_text="The frequency  of the light source (nm)")
    samples_per_pixel = models.IntegerField(
        blank=True,
        null=True)
    binning = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        help_text="Was the detector binned for acquisition")
    detector = models.ForeignKey(
        "OmeDetector",
        on_delete=models.PROTECT,
        blank=True,
        null=True)
    detector_gain = models.FloatField(
        blank=True,
        null=True)
