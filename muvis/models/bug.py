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
from datetime import timedelta
import logging
import sh

from django.db import models
from django.utils.html import mark_safe
from scans.models.dataset_status import DATASET_ONLINE
BUGZILLA_BUG_BASE_URL = "https://muvis.soton.ac.uk/bugzilla/show_bug.cgi?id="

class MuvisBug(models.Model):
    class Meta:
        ordering = ["muvis_id"]
    muvis_id = models.IntegerField(
        primary_key=True,
        null=False,
        help_text="Muvis bug ID")
    title = models.CharField(
        max_length=255,
        null=False,
        db_index=True,
        help_text="Muvis bug title")
    status = models.ForeignKey(
        "BugzillaStatus",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="Status of muvis bug")
    resolution = models.ForeignKey(
        "BugzillaResolution",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="How the ticket was resolved")

    def __str__(self):
        return "{}-{}".format(self.muvis_id, self.title)

    def bugzilla_link(self, verbose=False):
        url = "{}{}".format(BUGZILLA_BUG_BASE_URL, self.muvis_id)
        if verbose:
            return mark_safe('<a href="{url}">{url}</a>'.format(url=url))
        return mark_safe('<a href="{}">{}</a>'.format(url, self.muvis_id))

    def verbose_link(self):
        return self.bugzilla_link(True)
    verbose_link.short_description = "Bugzilla link"

    def no_scans(self):
        return self.scan_set.count()
    no_scans.short_description = "Number of scans associated with this bug"

    def estimate_total_scan_time(self):
        time = timedelta(seconds=0)
        for scan in self.scan_set.all():
            scan_time = scan.estimate_time()
            if scan_time:
                time += scan_time
        return time
    estimate_total_scan_time.short_description = "Estimate of the total scanning time for this bug"

    def get_directories(self):
        dir_list = []
        for scan in self.scan_set.all():
            if scan.dataset_status == DATASET_ONLINE:
                dir_list.append(scan.get_directory())
        return dir_list

    def disk_usage(self):
        dir_list = self.get_directories()
        if not dir_list:
            return 0
        dir_list_uniq = list(set(dir_list))
        try:
            return int(sh.du(*dir_list_uniq, "-sc").rstrip() \
               .split("\n")[-1:][0].split("\t")[0]) * 1024
        except sh.ErrorReturnCode_1 as exp:
            logger = logging.getLogger("Bug Disk usage")
            logger.error(str(exp))
            return None
    disk_usage.short_description = "Disk used"
