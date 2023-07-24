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
from django.utils.html import mark_safe
from django.urls import reverse
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from private_storage.fields import PrivateFileField


class SampleReport(models.Model):
    """
        Things needed to create a report document for a specific scan
    """
    EXCLUDED = "EX"
    BODY = "BD"
    APPENDIX = "AX"
    POSITION_OPTIONS = [(EXCLUDED, "Excluded"), (BODY,"Body"), (APPENDIX, "Appendix")]

    class Meta:
        unique_together = [["sample", "project", "date_generated"]]

    def get_subfolder(self):
        return [self.sample.xrh_id(), self.project.pk, self.pk]

    sample = models.ForeignKey(
        "Sample",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        db_index=True)
    project = models.ForeignKey(
        "projects.Project",
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    date_generated = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True)
    report = PrivateFileField(
        "Report",
        upload_to="sample_reports",
        upload_subfolder=get_subfolder,
        content_types=["application/pdf"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT)
    further_analysis_text = models.TextField(
        blank=True,
        null=True)
    generation_warnings = models.TextField(
        blank=True,
        null=True)
    generation_errors = models.TextField(
        blank=True,
        null=True)
    generation_success = models.BooleanField(
        blank=True,
        null=True)
    yz_slice_roll_position = models.CharField(
        max_length=2,
        verbose_name = "YZ slice roll position",
        choices=POSITION_OPTIONS,
        default=APPENDIX)
    xz_slice_roll_position = models.CharField(
        max_length=2,
        verbose_name = "XZ slice roll position",
        choices=POSITION_OPTIONS,
        default=BODY)
    xy_slice_roll_position = models.CharField(
        max_length=2,
        verbose_name = "XY slice roll position",
        choices=POSITION_OPTIONS,
        default=BODY)
    thick_slice_mip_position = models.CharField(
        max_length=2,
        verbose_name = "Thick slice MIP position",
        choices=POSITION_OPTIONS,
        default=BODY)
    thick_slice_avg_position = models.CharField(
        max_length=2,
        verbose_name = "Thick slice Average position",
        choices=POSITION_OPTIONS,
        default=APPENDIX)
    thick_slice_sum_position = models.CharField(
        verbose_name = "Thick slice Sum position",
        max_length=2,
        choices=POSITION_OPTIONS,
        default=EXCLUDED)
    mip_3d_position = models.CharField(
        verbose_name = "3D MIP position",
        max_length=2,
        choices=POSITION_OPTIONS,
        default=BODY)
    volume_3d_position = models.CharField(
        verbose_name = "3D Volume position",
        max_length=2,
        choices=POSITION_OPTIONS,
        default=BODY)
    xray_360_position = models.CharField(
        verbose_name = "X-Ray 360 position",
        max_length=2,
        choices=POSITION_OPTIONS,
        default=EXCLUDED)
    additional_videos_position = models.CharField(
        verbose_name = "Additional video(s) position",
        max_length=2,
        choices=POSITION_OPTIONS,
        default=EXCLUDED)
    thick_slice_stdev_position = models.CharField(
        verbose_name = "Thick Slice StDev position",
        max_length=2,
        choices=POSITION_OPTIONS,
        default=APPENDIX)

    returned_photos = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        help_text="Include the returned photos in an appendix")
    generic_photos = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        help_text="Include the generic photos in an appendix")
    projections = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        help_text="Include the system generated 0 and 90 degree projections")
    xy_slice = models.BooleanField(
        verbose_name="XY slice",
        default=False,
        null=False,
        blank=False,
        help_text="Include the system generated XY slice")
    generated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Who requested the report, blank if auto generated by the system")

    def __str__(self):
        return "{} {}".format(self.sample.xrh_id(), self.date_generated)

    def all_videos_excluded(self):
        return (
            self.yz_slice_roll_position == self.EXCLUDED and
            self.xz_slice_roll_position == self.EXCLUDED and
            self.xy_slice_roll_position == self.EXCLUDED and
            self.thick_slice_mip_position  == self.EXCLUDED and
            self.thick_slice_avg_position == self.EXCLUDED and
            self.thick_slice_sum_position == self.EXCLUDED and
            self.mip_3d_position == self.EXCLUDED and
            self.volume_3d_position == self.EXCLUDED and
            self.xray_360_position == self.EXCLUDED and
            self.thick_slice_stdev_position == self.EXCLUDED and
            self.additional_videos_position == self.EXCLUDED)

    def count_video_types(self):
        fields = [
            self.yz_slice_roll_position,
            self.xz_slice_roll_position,
            self.xy_slice_roll_position,
            self.thick_slice_mip_position,
            self.thick_slice_avg_position,
            self.thick_slice_sum_position,
            self.mip_3d_position,
            self.volume_3d_position,
            self.xray_360_position,
            self.thick_slice_stdev_position,
            self.additional_videos_position,
        ]
        count = 0
        for field in fields:
            if field != self.EXCLUDED:
                count += 1
        return count
    count_video_types.short_decription = "Number of different videos included"

    def clean(self):
        for scan_map in self.reportscanmapping_set.all():
            if self.sample != scan_map.scan.sample:
                raise ValidationError(_('Scan is not of sample'))

    def date_generated_link(self):
        url = reverse('admin:samples_samplereport_change', args=[self.pk])
        if self.date_generated:
            return mark_safe('<a href="{}">{}</a>'.format(
                url, self.date_generated.strftime("%Y-%m-%d  %T %Z")))
        return mark_safe('<a href="{}">PENDING</a>'.format(url))
    date_generated_link.short_description = "Date Generated"
    date_generated_link.admin_order_field = date_generated

class ReportScanMapping(models.Model):
    class Meta:
        unique_together = [["report", "scan"]]

    report = models.ForeignKey(
        "SampleReport",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_index=True)
    scan = models.ForeignKey(
        "scans.Scan",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_index=True)

    def clean(self):
        try:
            sample_id_no = self.report.sample.xrh_id_number
            scan_sample_id_no = self.scan.sample.xrh_id_number
            if sample_id_no != scan_sample_id_no:
                #Only use the numeric part because a slide has a different suffix
                #This allows scans from multiple states to be included in the same report
                raise ValidationError(_("Scan is not of sample"))
        except ObjectDoesNotExist:
            pass

    def generation_success(self):
        return self.report.generation_success
    generation_success.boolean = True

    def link(self):
        url = reverse('admin:samples_samplereport_change', args=[self.report_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, str(self.report)))
    link.short_description = "Report"

    def scan_id_link(self):
        url = reverse('admin:scans_scan_change', args=[self.scan_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.scan_id))
    scan_id_link.short_description = "Scan ID"
    scan_id_link.admin_order_field = "scan"
