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
from django.db import models
from django.utils.html import mark_safe
from django.urls import reverse

class ScheduledMove(models.Model):
    class Meta:
        verbose_name = "Scheduled dataset moves"
        verbose_name_plural = "Scheduled dataset moves"

    scan = models.ForeignKey(
        "Scan",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
    destination = models.ForeignKey(
        "Share",
        on_delete=models.PROTECT,
        blank=False,
        null=False)
    group_by_sample = models.BooleanField(
        default=True,
        null=False,
        blank=False)
    date_queued = models.DateTimeField(
        db_index=True,
        auto_now_add=True)
    date_executed = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True)
    success = models.BooleanField(
        blank=True,
        null=True)
    output = models.TextField(
        blank=True,
        null=True)

    def __str__(self):
        return "{} -> {}".format(self.scan, self.destination)

    def scan_link(self):
        url = reverse('admin:scans_scan_change', args=[self.scan_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, str(self.scan)))
    scan_link.short_description = "Scan"
    scan_link.admin_order_field = "scan"
