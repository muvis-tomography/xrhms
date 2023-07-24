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

    A model to contain data that applies to all scans no matter what machine they are from
"""
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import sh
from django.db import models
from django.utils.html import mark_safe
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from private_storage.fields import PrivateFileField

from polymorphic.models import PolymorphicModel
from .dataset_status import (
    DATASET_STATUS_CHOICES,
    DATASET_DELETED,
    DATASET_ONLINE,
    DATASET_MISSING,
#    CAN_CHECK_STATUS_LIST,
    DATASET_ARCHIVED_MUVIS,
    DATASET_ARCHIVED_DISK
)

SIDECAR_SUFFIX = "xrhms"
class SidecarStatus(Enum):
    OK = 0
    MOVED = 1
    COPIED = 2
    MISSING = 3
    INVALID = 4


class Scan(PolymorphicModel):
    def get_subfolder(self):
        return [self.pk]

    class Meta:
        unique_together = [
            ["share", "path", "filename"]
        ]
        index_together = [
            "share", "path"
        ]
    scan_date = models.DateField(
        db_index=True,
        blank=False,
        null=False)
    inserted = models.DateTimeField(
        db_index=True,
        auto_now_add=True)
    scanner = models.ForeignKey(
        "Machine",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
    operator = models.CharField(
        max_length=30,
        blank=True,
        null=True)
    sample = models.ForeignKey(
        "samples.Sample",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="The sample that this scan relates to")
    share = models.ForeignKey(
        "Share",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
    path = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Path on the specified share to the share")
    filename = models.CharField(
        max_length=255,
        db_index=True,
        blank=False,
        null=False)
    muvis_bug = models.ForeignKey(
        "muvis.MuvisBug",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The Muvis Bug relating to the scan")
    checksum = models.CharField(
        max_length=64,
        db_index=True,
        blank=False,
        null=False)
    name = models.CharField(
        max_length=255,
        db_index=True)
    src_to_object = models.FloatField(
        blank=True,
        null=True)
    src_to_detector = models.FloatField(
        blank=True,
        null=True)
    detector_pixels_x = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Detector pixels X")
    detector_pixel_size_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Detector pixel size X")
    detector_pixels_y = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Detector pixels Y")
    detector_pixel_size_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Detector pixel size Y")
    xray_kv = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="X-Ray Voltage (kV)")
    xray_ua = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="X-Ray Current (µA)")
    projection0deg = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/tiff"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    projection0deg_png = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    projection90deg = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/tiff"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    projection90deg_png = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    xyslice = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/tiff"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    xyslice_png = PrivateFileField(
        "Attachment",
        upload_to="scan",
        upload_subfolder=get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    projections = models.IntegerField(
        blank=True,
        null=True)
    frames_per_projection = models.IntegerField(
        blank=True,
        null=True)
    initial_angle = models.FloatField(
        blank=True,
        null=True)
    notes = models.TextField(
        blank=True,
        null=True)
    dataset_status = models.CharField(
        max_length=2,
        choices=DATASET_STATUS_CHOICES,
        default=DATASET_ONLINE,
        blank=False,
        null=False)
    dataset_status_last_updated = models.DateTimeField(
        auto_now_add=True)
    extra_listing = models.TextField(
        blank=True,
        null=True,
        help_text="Files in the extra folder")
    extra_listing_last_updated = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the listing for the extra folder was last updated")
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        help_text="The scan object that this one is derived from")


    def __str__(self):
        return "({}) {}".format(self.pk, self.name)


    def power(self):
        try:
            return self.xray_ua * self.xray_kv /1000
        except TypeError:
            return None
    power.short_description = "Power (W)"

    def scan_id_link(self):
        url = reverse('admin:scans_scan_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.pk))
    scan_id_link.short_description = "Scan ID"
    scan_id_link.admin_order_field = "scan_id"

    def scan_link(self):
        url = reverse('admin:scans_scan_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, str(self)))
    scan_link.short_description = "Name"
    scan_link.admin_order_field = "name"

    def parent_link(self):
        if self.parent:
            url = reverse('admin:scans_scan_change', args=[self.parent_id])
            return mark_safe('<a href="{}">{}</a>'.format(url, str(self.parent)))
        return "-"
    parent_link.short_description = "Parent"
    parent_link.admin_order_field = "parent"

    def name_link(self):
        url = reverse('admin:scans_scan_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.name))
    name_link.short_description = "Name"
    name_link.admin_order_field = "name"

    def filename_link(self):
        url = reverse('admin:scans_scan_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.filename))
    filename_link.short_description = "Filename"
    filename_link.admin_order_field = "filename"

    def muvis_bug_link(self):
        url = reverse('admin:muvis_muvisbug_change', args=[self.muvis_bug.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, str(self.muvis_bug)))
    muvis_bug_link.short_description = "Muvis Bug"
    muvis_bug_link.admin_order_field = "muvis_bug"


    def get_directory(self):
        return Path(self.share.linux_mnt_point, self.path) #pylint:disable=no-member

    def scanner_link(self):
        url = reverse('admin:scans_machine_change', args=[self.scanner_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.scanner))
    scanner_link.short_description = "Scanner"
    scanner_link.admin_order_field = "scanner"

    def share_link(self):
        url = reverse('admin:scans_share_change', args=[self.share_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.share))
    share_link.short_description = "Share"
    share_link.admin_order_field = "Share"

    def sample_link(self):
        if self.sample:
            url = reverse('admin:samples_sample_change', args=[self.sample.pk])
            return mark_safe('<a href="{}">{}</a>'.format(url, self.sample))
        return "-"
    sample_link.short_description = "Sample"
    sample_link.admin_order_field = "sample"

    def internal_mnt_path(self):
        internal = self.share.internal_mnt_path() #pylint:disable=no-member
        if internal == "-":
            return "-"
        return "{}/{}".format(internal, self.path).replace("/", "\\")
    internal_mnt_path.short_description = "Internal mount path"

    def internal_ipv4_mnt_path(self):
        internal = self.share.internal_ipv4_mnt_path() #pylint:disable=no-member
        if internal == "-":
            return "-"
        return "{}/{}".format(internal, self.path).replace("/", "\\")
    internal_ipv4_mnt_path.short_description = "Internal IPv4 mount path"

    def internal_ipv6_mnt_path(self):
        internal = self.share.internal_ipv6_mnt_path() #pylint:disable=no-member
        if internal == "-":
            return "-"
        return "{}/{}".format(internal, self.path).replace("/", "\\")
    internal_ipv6_mnt_path.short_description = "Internal IPv6 mount path"

    def external_mnt_path(self):
        external = self.share.external_mnt_path() #pylint:disable=no-member
        if external == "-":
            return "-"
        return "{}/{}".format(external, self.path).replace("/", "\\")
    external_mnt_path.short_description = "External mount path"

    def external_ipv4_mnt_path(self):
        external = self.share.external_ipv4_mnt_path() #pylint:disable=no-member
        if external == "-":
            return "-"
        return "{}/{}".format(external, self.path).replace("/", "\\").replace("/", "\\")
    external_ipv4_mnt_path.short_description = "External IPv4 mount path"

    def external_ipv6_mnt_path(self):
        external = self.share.external_ipv6_mnt_path() #pylint:disable=no-member
        if external == "-":
            return "-"
        return "{}/{}".format(external, self.path).replace("/", "\\").replace("/", "\\")
    external_ipv6_mnt_path.short_description = "External IPv6 mount path"

    def file_available(self):
        if self.dataset_status == DATASET_ONLINE:
            return "Yes"
        return "No"
    file_available.short_description = "File available"

    def full_path(self):
        return Path(self.share.linux_mnt_point, self.path, self.filename) #pylint:disable=no-member

    def check_exists(self):
        return self.full_path().exists()

    def update_exists(self):
        """
            return (exists, changed)
        """
        if self.dataset_status in [DATASET_ARCHIVED_MUVIS, DATASET_ARCHIVED_DISK]:
            ##These status may be online or not depending on mounted disk status - don't try to update
            return (self.dataset_status, False)
        new_status = self.check_exists()
        if new_status:
            expected_status = [DATASET_ONLINE]
        else:
            expected_status = [
                DATASET_MISSING, DATASET_DELETED, DATASET_ARCHIVED_DISK, DATASET_ARCHIVED_MUVIS
            ]
        change = self.dataset_status not in expected_status
        if change:
            if new_status:
                self.dataset_status = DATASET_ONLINE
            else:
                self.dataset_status = DATASET_MISSING
            self.dataset_status_last_updated = timezone.now()
            self.save()
        for refined in self.refinedrawdata_set.all():
            refined.update_exists()
        return (new_status, change)

    def scan_type(self):
        return self.polymorphic_ctype.name

    def save_sidecar(self):
        """
            save the metadata sidecar file to help with tracking moves / copies
        """
        filename = generate_sidecar_filename(self.full_path())
        data = {}
        data["pk"] = self.pk
        with open(filename, "w") as f_handle:
            json.dump(data, f_handle, sort_keys=True)

    def sidecar_correct(self):
        filename = generate_sidecar_filename(self.full_path())
        if not filename.exists():
            return False
        return self == load_sidecar(filename)
    def check_sidecar_status(self, actual_path):
        if self.full_path() == actual_path:
            sidecar_exists = generate_sidecar_filename(self.full_path()).exists()
            if not sidecar_exists:
                return SidecarStatus.MISSING
            sidecar_valid = self.sidecar_correct()
            if not sidecar_valid:
                return SidecarStatus.INVALID
            return SidecarStatus.OK
        #If get here then paths don't match - either moved or copied
        if self.full_path().exists():
            #original exists
            return SidecarStatus.COPIED
        return SidecarStatus.MOVED

    def validate_parent_candidate(self, candidate):
        """
            Check that the candidate is likely to be the parent.
            This plays it safe and won't link if there's any doubt
            Possible ways of checking:
                pk < self.pk
                    Only works on scans added in automatically may fail for medx etc.
                create_time < self.create_time
                    May not work for scans copied/moved in
                len(filename) < len(self.filename)
                    May be ok as additional recon will have extra contents in filename
                scan_data <= self.scan_date
                    will be equal if on same day
            No guaranteed way of doing it - may need manual intervention for some scans.
        """
        if candidate.pk > self.pk: # shouldn't happen in normal use
            return False
        if len(candidate.filename) > len(self.filename):
            return False
        if isinstance(candidate.scan_date, datetime) and isinstance(self.scan_date, datetime):
            if candidate.scan_date > self.scan_date:
                return False
        else:
            return False # can't perform datetime comparison - probably slide scans so not parents
        return True

    def find_parent(self):
        """
            Looks in the same folder to see if a parent scan exists.

            This comes about if a scan is reconstructed multiple times,
            of if the autorecon function isn't used.

            The parent is defined as the oldest scan in the same folder
        """
        same_folder = Scan.objects.filter(
            share = self.share,
            path = self.path).exclude(pk=self.pk) # don't include self in the list
        if same_folder.count == 0:
            # First scan in this folder therefore no parent
            self.parent = None
        elif same_folder.count == 1:
            candidate = same_folder[0]
            if self.validate_parent_candidate(candidate):
                self.parent = candidate
        else:
            #multiple potentials need to choose one
            same_folder = same_folder.order_by("pk")
            # sort by PK as it's likely parent will have lowest
            for candidate in same_folder:
                if self.validate_parent_candidate(candidate):
                    self.parent = candidate
                    break
        return bool(self.parent)


    def disk_usage(self):
        """
            Work out how much space it's using on disk in bytes
        """
        if self.dataset_status != DATASET_ONLINE:
            raise ValueError("Dataset must be online")
        return int(
            sh.du(self.full_path().parent, "-sc").split("\n")[-2].split("\t")[0]) * 1024

    def sample_info_filename(self):
        """
            Work out the sample information filename
        """
        filename = settings.SAMPLE_INFO_FILE
        parent = self.full_path().parent
        return Path(parent, filename)


    def generate_sample_info(self):
        """
            Generate a sample information file with a brief summary of information
            about the sample for keeping with the scan
        """
        filepath = self.sample_info_filename()
        parent = self.full_path().parent
        if not parent.exists():
           # self._logger.info("Skipping as no longer on disk")
            return
        #self._logger.debug("Using %s for filepath", filepath)
        if filepath.exists():
            #self._logger.info("File already exists must have been created previously")
            return
        sample = self.sample
        if not sample:
            #no sample linked so unable to generate
            return
        with open(filepath, "w") as f_handle:
            xrh_id = sample.full_xrh_id
            f_handle.write("XRH ID:\t\t{}\r\n".format(xrh_id))
            original_id = sample.original_id
            if original_id:
                f_handle.write("Original ID:\t{}\r\n".format(original_id.strip()))
            f_handle.write("Species:\t{}\r\n".format(sample.species))
            f_handle.write("Tissue:\t\t{}\r\n".format(sample.tissue))
            condition = sample.condition
            if condition:
                f_handle.write("Condition:\t{}\r\n".format(condition))
            f_handle.write("Sample type:\t{}\r\n".format(sample.sample_type))

def generate_sidecar_filename(path):
    filename = path.name
    sidecar_filename = "." + filename + "." + SIDECAR_SUFFIX
    return Path(path.parent, sidecar_filename)

def load_sidecar(path):
    if not path.exists():
        raise FileNotFoundError("Path ({}) does not exist".format(str(path)))
    with open(path, "r") as f_handle:
        data = json.load(f_handle)
        pk = data["pk"] #pylint:disable=invalid-name
        return Scan.objects.get(pk=pk)
