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
from pathlib import Path

from django.db import models
from django.conf import settings

from private_storage.fields import PrivateFileField
from xrh_utils import generate_qr_code

class ArchiveDrive(models.Model):

    def get_subfolder(self):
        return [self.pk]

    date_created = models.DateTimeField(
        auto_now_add=True)
    serial_number = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
        null=True)
    manufacturer = models.CharField(
        max_length=40,
        blank=True,
        null=True)
    capacity = models.FloatField(
        blank=True,
        null=True,
        help_text="Capacity in GB")
    estimated_usage = models.FloatField(
        blank=True,
        null=True,
        default=0,
        help_text = "Estimated disk usage in GB")
    no_files = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        help_text="Number of files on the drive")

    qr_code = PrivateFileField(
        "QR code",
        upload_to="archive_drive",
        upload_subfolder = get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    scans = models.ManyToManyField(
        "Scan",
        blank=True,
        through="ScanArchive")

    def __str__(self):
        return "Archive disk {}".format(self.pk)

    def estimated_free(self):
        return self.capacity - self.estimated_usage

    def save(self, *args, **kwargs): #pylint: disable=signature-differs
        new_entry =  (not self.pk)
        super().save(*args, **kwargs)
        if new_entry:
            self._add_qr_code()

    def _add_qr_code(self, force=False):
        if force or self.qr_code.name is None or self.qr_code.name == "":
            if force:
                self.qr_code.delete()
            #Check it isn't already in existance unless being force
            (temp_dir, fname) = generate_qr_code(self.url())
            self.qr_code.save(fname, open(Path(temp_dir.name, fname), "rb"))
            self.save()

    def url(self):
        return "https://{}/ms/a/sc/ad/{}".format(
            settings.ALLOWED_HOSTS[0],
            self.pk)

class ScanArchive(models.Model):
    class Meta:
        unique_together = [("scan", "drive", "path")]
    scan = models.ForeignKey(
        "Scan",
        on_delete=models.PROTECT)
    drive = models.ForeignKey(
        "ArchiveDrive",
        on_delete=models.PROTECT)
    date_indexed =  models.DateTimeField(
        auto_now_add=True)
    path = models.CharField(
        max_length=255,
        null=False,
        blank=False)
    total_size = models.FloatField(
        blank=True,
        null=True,
        help_text="The size of the folder and subtree on the disk (GiB)")
    file_count = models.IntegerField(
        blank=True,
        null=True,
        help_text="The number of files in this folder and subtree")
