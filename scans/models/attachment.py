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

ALLOWED_TYPES = settings.ATTACHMENT_TYPES
ALLOWED_TYPES += [
    "application/xml", # ctprofile
    "text/plain",   #angle file
]

class ScanAttachment(models.Model):

    NONE = "NA"
    TOP_LEFT = "TL"
    TOP_RIGHT = "TR"
    BOTTOM_LEFT = "BL"
    BOTTOM_RIGHT = "BR"

    OVERLAY_POSITION_OPTIONS = [
        (NONE, "None"),
        (TOP_LEFT, "Top Left"),
        (TOP_RIGHT, "Top Right"),
        (BOTTOM_LEFT, "Bottom Left"),
        (BOTTOM_RIGHT, "Bottom Right")
    ]

    def get_subfolder(self):
        return [self.scan_id]

    attachment_type = models.ForeignKey(
        "ScanAttachmentType",
        on_delete=models.PROTECT,
        null=True,
        blank=True)
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
    url = models.URLField(
        max_length=255,
        verbose_name = "URL",
        blank=True,
        null=True,
        help_text="URL for viewing the resource externally.")
    checksum = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        null=True,
        help_text="Checksum for automatically ingested files")
    to_upload = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Should this be uploaded to be made public")
    overlay_position = models.CharField(
        max_length = 2,
        verbose_name="Video overlay position",
        default=NONE,
        choices=OVERLAY_POSITION_OPTIONS,
        help_text="If this is publically uploaded where to put the XRH logo")
    exclude_from_report = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Exclude this from the report even if it is a valid attachment type")
    editable = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        help_text="Can the user edit this attachment")
    scan = models.ForeignKey(
        "Scan",
        on_delete=models.CASCADE,
        null=False,
        blank=False)
    attachment = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=settings.ATTACHMENT_TYPES,
        max_file_size=settings.LARGE_ATTACHMENT_FILE_SIZE_LIMIT)

    def publically_uploaded(self):
        return self.url is not None
    publically_uploaded.short_description = "Upload complete"
    publically_uploaded.boolean = True



    def __str__(self):
        return "{}-{}-{}".format(self.scan, self.attachment_type, self.name)

    def name_link(self):
        url = reverse('admin:scans_scanattachment_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.name))
    name_link.short_description = "Name"
    name_link.admin_order_field = "name"

    def preview(self):
        if self.is_image():
            return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint: disable=line-too-long
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


class ScanAttachmentType(models.Model):
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
    report_priority = models.IntegerField( # negative priority are excluded from report
        null=False,
        blank=False,
        unique=True,
        help_text="Priority for ordering when putting in a report")
    include_in_extra_folder = models.BooleanField(
        null=False,
        blank=False,
        help_text="Include when exporting to an extra folder",
        default=True)
    def __str__(self):
        return self.name

class ScanAttachmentTypeSuffix(models.Model):
    """
        The end of the filename that conicide with the type
    """
    attachment_type = models.ForeignKey(
        "ScanAttachmentType",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="The attachment type this relates to")
    suffix = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        unique=True,
        help_text="The string to look for in filenames")

    def __str__(self):
        return self.suffix
