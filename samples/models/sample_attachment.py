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
import imghdr
import mimetypes
from django.db import models
from django.utils.html import mark_safe
from django.conf import settings
from django.urls import reverse

from private_storage.fields import PrivateFileField

PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600

class SampleAttachment(models.Model):

    def get_subfolder(self):
        return [self.sample.xrh_id()]

    sample = models.ForeignKey(
        "Sample",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        db_index=True)
    attachment_type = models.ForeignKey(
        "SampleAttachmentType",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="The type of the attachment")
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Short name for the attachment")
    uploaded = models.DateTimeField(
        auto_now_add=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about the attachment")
    attachment = PrivateFileField(
        "Attachment",
        upload_to="sample",
        upload_subfolder=get_subfolder,
        content_types=settings.ATTACHMENT_TYPES,
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT)

    def __str__(self):
        return "{}-{}-{}".format(
            self.sample,
            self.attachment_type,
            self.name)

    def name_link(self):
        url = reverse('admin:samples_sampleattachment_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.name))
    name_link.admin_order_field = "name"
    name_link.short_description  = "Name"

    def preview(self):
        if self.is_image():
            return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint:disable=line-too-long
                self.attachment.url,
                self.attachment.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
        if self.is_video():
            html = '<video width="{}" height="{}" controls>'.format(PREVIEW_WIDTH, PREVIEW_HEIGHT)
            html += '<source src="{}" type="video/mp4">'.format(self.attachment.url)
            html += 'Preview unsupported <a href="{}">{}</a>'.format(
                self.attachment.url, self.attachment.url)
            html += "</video>"
            return mark_safe(html)
        return "-"

    def is_image(self):
        return bool(imghdr.what(self.attachment.file))
    is_image.boolean = True

    def is_video(self):
        return mimetypes.guess_type(self.attachment.file.name)[0] in settings.VIDEO_TYPES
    is_video.boolean = True

class SampleAttachmentType(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=False,
        null=False,
        help_text="Name for the attachment type")
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the attachment type")

    def __str__(self):
        return self.name
