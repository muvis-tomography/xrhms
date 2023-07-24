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
from django.contrib.auth import get_user_model

class Location(models.Model):
    """
        Places where a sample may be stored
    """
    name = models.CharField(
        max_length=50,
        db_index=True,
        unique=True,
        help_text="The name of the location / status")
    location = models.CharField(
        max_length=50,
        unique=True,
        blank = True,
        null = True,
        help_text="The location of the place. eg SGH/LA68")
    description = models.TextField(
        blank=True,
        help_text="More details about the location / status")
    our_control = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        help_text="Is this a location that we control. I.e. are samples in this location in our custody") #pylint: disable=line-too-long

    class Meta:
        verbose_name = "Location / Status"
        verbose_name_plural = "Locations / Statuses"

    def __str__(self):
        """
            Just use the sample name as the string representation
        """
        return self.name

class SampleLocationMapping(models.Model):
    """
        Store a record of where a sample is at any given time
    """
    sample = models.ForeignKey(
        "Sample",
        on_delete=models.PROTECT,
        help_text="The sample this status refers to")
    location = models.ForeignKey(
        "Location",
        on_delete=models.PROTECT,
        help_text="The location / status")
    date_entered = models.DateTimeField(
        db_index = True,
        verbose_name="Date",
        auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name="By",
        blank=True,
        help_text="The user who made the change")
    notes = models.TextField(
        blank=True,
        help_text="Any additional information")


    def __str__(self):
        return "{} {} {} {}".format(
            self.sample.xrh_id(), self.location.name,
            self.date_entered.strftime("%Y-%m-%d %H:%M:%S"), self.user)
