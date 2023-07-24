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

class StorageRequirement(models.Model):
    """
        Requirements about how the sample has to be stored
    """
    name = models.CharField(
        max_length=50,
        db_index=True,
        unique=True,
        verbose_name="Name",
        help_text="Short name for the requirements")

    details = models.TextField(
        blank=True,
        help_text="Long form description of the requirements")

    def __str__(self):
        """
            Overwrite the default representation
        """
        return self.name