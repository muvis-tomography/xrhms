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

    Attachments for Sample types so can be used to store RA / MS etc
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.html import mark_safe
from private_storage.fields import PrivateFileField

class SampleTypeAttachment(models.Model):

    def get_subfolder(self):
        return [self.sample_type_id]

    sample_type = models.ForeignKey(
        "SampleType",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
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
        upload_to="sample_type",
        upload_subfolder=get_subfolder,
        content_types=settings.ATTACHMENT_TYPES,
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT)

    def __str__(self):
        return "{} {}".format(self.name, self. uploaded)

    def name_link(self):
        url = reverse('admin:samples_sampletypeattachment_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.name))
    name_link.admin_order_field = "name"
    name_link.short_description  = "Name"
