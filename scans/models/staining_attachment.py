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
from django.conf import settings
from private_storage.fields import PrivateFileField

class StainingAttachment(models.Model):
    def get_subfolder(self):
        return [self.protocol_id]

    protocol = models.ForeignKey(
        "Staining",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False)
    attachment = PrivateFileField(
        "Attachment",
        upload_to="staining",
        content_types=settings.ATTACHMENT_TYPES,
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=False,
        null=False)
    notes = models.TextField(
        blank=True,
        null=True)
