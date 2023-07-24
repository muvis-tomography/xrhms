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
from django.conf import settings
from django.db import models
from private_storage.fields import PrivateFileField

class OmePlane(models.Model):
    def get_subfolder(self):
        return [self.image.scan_id, self.image_id]

    class Meta:
        verbose_name = "OME Plane"
        verbose_name_plural = "OME Planes"
    exposure = models.FloatField(
        blank=True,
        null=True,
        help_text="exposure time (s)")
    position_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name = "Position X",
        help_text="X position in µm")
    position_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name = "Position Y",
        help_text="Y position in µm")
    channel = models.ForeignKey(
        "OmeChannel",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The channel used for illumination")
    t = models.IntegerField(
        blank=True,
        null=True,
        help_text="Time interval for image")
    z = models.IntegerField(
        blank=True,
        null=True,
        help_text="Z position")
    preview = PrivateFileField(
        "PlanePreview",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    filename = models.CharField(
        max_length=255,
        blank=False,
        null=False)
    image = models.ForeignKey(
        "OmeImage",
        on_delete=models.CASCADE,
        blank=False,
        null=False)


    def __str__(self):
        return "Plane {}".format(self.pk)
