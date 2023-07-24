#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use,too-many-public-methods
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
from datetime import timedelta
from pathlib import Path


from django.db import models
from django.conf import settings
from django.utils import timezone

from xrh_utils import directory_size

class UserCopy(models.Model):
    class Meta:
        verbose_name_plural = "User Copies"
        unique_together = [
            ("scan", "username", "date_added")
        ]
    scan = models.ForeignKey(
        "Scan",
        on_delete = models.PROTECT,
        null=False,
        blank=False)
    include_recon_data = models.BooleanField(
        default=True,
        null=False,
        blank=False,
        help_text="Copy the reconstructed data folder")
    include_raw_data = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        help_text="Copy the raw projections")
    username = models.CharField(
        db_index=True,
        null=False,
        blank=False,
        max_length=30,
        help_text="The user to make the files available to")
    date_added = models.DateTimeField(
        auto_now_add=True)
    date_copied = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the data was copied to the user store")
    copy_success = models.BooleanField(
        db_index=True,
        blank=True,
        null=True)
    deletion_after = models.IntegerField(
        blank=False,
        null=False,
        default=settings.DEFAULT_USER_COPY_DELETION_DAYS,
        help_text="How many days to leave available for (minimum)")
    cmd_output = models.TextField(
        blank=True,
        null=True,
        help_text="Output from the various commands")
    date_deleted = models.DateTimeField(
        blank=False,
        null=True,
        help_text="When the files were removed")
    deletion_success = models.BooleanField(
        db_index=True,
        null=True,
        blank=True)

    def __str__(self):
        return "{} scan {}".format(self.username, self.scan_id)

    def deletion_valid_from(self):
        if not self.date_copied:
            raise ValueError("Unable to calculate as not yet copied")
        return self.date_copied.date() + timedelta(days=self.deletion_after)

    def deletion_eligible(self):
        if not self.date_copied: # not attempted to copy it
            return False
        if not self.copy_success: # failed to copy so nothing to delete
            return False
        if self.date_deleted: # already attempted to delete it no point trying again
            return False
        #Only now do we have to do actual maths
        return (timezone.now().date() - self.date_copied.date()) > \
            timedelta(days=self.deletion_after)

    def folder_name(self):
        return Path(
            settings.USER_DATA_FOLDER,
            self.username,
            "{}_{}".format(self.scan.name, self.pk))

    def size_on_disk(self):
        return directory_size(self.folder_name())

    def changelog_file_name(self):
        return Path(
            settings.USER_DATA_FOLDER,
            self.username,
            "CHANGELOG.txt")
