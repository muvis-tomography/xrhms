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

class Gain(models.Model):
    class Meta:
        verbose_name = "Scanner Gain"
        verbose_name_plural = "Scanner Gains"
        unique_together = [["scanner", "gain_type", "index"]]
    ANALOG = "ANA"
    DIGITAL = "DIG"
    GAIN_TYPE_CHOICES = [
        (ANALOG, "Analog"),
        (DIGITAL, "Digital")
    ]
    scanner = models.ForeignKey(
        "Machine",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
    gain_type = models.CharField(
        max_length=3,
        choices=GAIN_TYPE_CHOICES,
        blank=False,
        null=False)
    index = models.IntegerField(
        blank=False,
        null=False,
        help_text="The array index used in the xtekct file")
    value = models.IntegerField(
        blank=False,
        null=False,
        help_text="The real world value in dB")

    def __str__(self):
        return "{} - {} {}:{}".format(self.scanner, self.gain_type, self.index, self.value)
