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

class SampleType(models.Model):
    """
        Describes the type of the sample.
        Expected values include:
        Fresh
        Frozen
        Slide
        Virtual
    """
    name = models.CharField(
        max_length=50,
        db_index=True,
        unique=True,
        help_text="Short name for the type. eg. 'fresh'",
        verbose_name="Name")
    suffix = models.CharField(
        max_length=10,
        db_index=True,
        unique=True,
        help_text="Suffix to apply to sample IDs")
    description = models.TextField(
        blank=True,
        help_text="Long form description")
    additional_risks = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        help_text="Is this sample type subject to additional Risk Assessment")

    def __str__(self):
        """
            Overwrite the default representation
        """
        return self.name
