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

class Machine(models.Model):
    class Meta:
        verbose_name = "Scanner"
        verbose_name_plural = "Scanners"
    name = models.CharField(
        max_length=50,
        db_index=True,
        unique=True)
    shuttle_multiplier = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Shuttling multiplier",
        help_text="Factor to use when calculating how long a scan will take with shuttling")

    def __str__(self):
        return self.name
