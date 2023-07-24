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
from django.contrib.auth import get_user_model

from private_storage.fields import PrivateFileField

from .status import ProjectUpdate

PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600



class ProjectAttachment(models.Model):
    class Meta:
        unique_together = [["project", "name"]]
    def get_subfolder(self):
        return [self.project_id]

    project = models.ForeignKey(
        "Project",
        on_delete=models.PROTECT)
    description = models.TextField(
        blank=True,
        null=True)
    attachment = PrivateFileField(
        "Attachment",
        upload_to="project",
        upload_subfolder=get_subfolder,
        content_types=settings.ATTACHMENT_TYPES,
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT)
    name = models.CharField(
        max_length=255,
        db_index = True,
        blank=False,
        null=False)
    uploaded = models.DateTimeField(
        auto_now_add=True)
    uploaded_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        default=settings.SUPER_USER_ID,
        null=False,
        blank=True)


    def __str__(self):
        return "{} - {}".format(self.project.name, self.name)

    def save(self, *args, **kwargs): #pylint: disable=signature-differs
        super().save(*args, **kwargs) # save the object
        update = ProjectUpdate()
        update.project = self.project
        update.last_action_date = self.uploaded
        update.last_action = "Attachment {} added".format(self.name)
        update.user = self.uploaded_by
        update.clean()
        update.save()
        update.send_update_emails()

    def preview(self):
        if self.is_image():
            return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint: disable=line-too-long
                self.attachment.url,
                self.attachment.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
        if self.is_video():
            html = '<video style="max-width:{}px; max-height:{}px;" controls>'.format(
                PREVIEW_WIDTH, PREVIEW_HEIGHT)
            html += '<source src="{}" type="video/mp4">'.format(self.attachment.url)
            html += 'Preview unsupported <a href="{}">{}</a>'.format(
                self.attachment.url, self.attachment.url)
            html += "</video>"
            return mark_safe(html)
        return ""

    def is_image(self):
        return bool(imghdr.what(self.attachment.file))
    is_image.boolean = True

    def is_video(self):
        return mimetypes.guess_type(self.attachment.file.name)[0] in settings.VIDEO_TYPES
    is_video.boolean = True
