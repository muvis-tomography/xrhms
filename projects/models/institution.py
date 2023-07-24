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

class Institution(models.Model):
    """
        An organisation that a contact and/or project can be affiliated to
    """
    name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Name of the Organisation",
        unique=True,
        verbose_name="Name")
    url = models.URLField(
        blank=True,
        verbose_name="Organisation website",
        help_text="Link to the organisation website")
    notes = models.TextField(
        blank="True",
        help_text="Additional notes")

    def __str__(self):
        """
            Override the default text representation"
        """
        return self.name
