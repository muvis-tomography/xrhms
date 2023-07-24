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
from datetime import datetime
import os
import imghdr
from django.utils.html import mark_safe

from django.conf import settings
from django.db import models
from private_storage.fields import PrivateFileField

PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600


class ScannerScreenshot(models.Model):
    class Meta():
        unique_together = (("scanner", "screen_number"))


    def get_subfolder(self):
        return [self.scanner_id]

    scanner = models.ForeignKey(
        "Machine",
        verbose_name = "Scanner",
        on_delete=models.PROTECT,
        null=False,
        blank=False)
    screen_number = models.IntegerField(
        default=1,
        null=False,
        blank=False)
    attachment = PrivateFileField(
        "screenshot",
        upload_to="scanner",
        blank=False,
        null=False,
        upload_subfolder=get_subfolder,
        content_types=settings.ATTACHMENT_TYPES,
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT)

    def image_timestamp(self):
        try:
            filename = self.attachment.path
            return datetime.fromtimestamp(os.path.getmtime(filename))
        except: #pylint: disable=bare-except
            return None
    image_timestamp.short_description = "Image timestamp"

    def __str__(self):
        return "{}:{}".format(self.scanner, self.screen_number)

    def preview(self):
        if self.is_image():
            return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint:disable=line-too-long
                self.attachment.url,
                self.attachment.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
        return None

    def is_image(self):
        return bool(imghdr.what(self.attachment.file))
    is_image.boolean = True
