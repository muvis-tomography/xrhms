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


class Contact(models.Model):
    """
        Class to describe any percon outside the project that is interacted with.
    """
    name = models.CharField(
        max_length=200,
        db_index=True,
        unique=True,
        help_text="Name of the person",
        verbose_name="Name")
    email = models.EmailField(
        max_length=200,
        blank=True,
        help_text="Email address used to contact the person",
        verbose_name="Email address")
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Phone Number",
        help_text="Contact phone number to use")
    address = models.TextField(
        blank=True,
        verbose_name="Postal address",
        help_text="Address to send samples to")
    notes = models.TextField(
        blank="True",
        help_text="Additional notes")
    affiliation = models.ManyToManyField(
        "Institution",
        blank=True,
        help_text="Linked Organisations")
    url = models.URLField(
        blank=True,
        verbose_name="Personal website",
        help_text="Link to their website")

    def __str__(self):
        """
            Override the default text representation"
        """
        return self.name
