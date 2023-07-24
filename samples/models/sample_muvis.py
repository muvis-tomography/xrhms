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

class SampleMuvisMapping(models.Model):
    sample = models.ForeignKey(
        "Sample",
        on_delete=models.PROTECT,
        null=False,
        blank=False)
    bug = models.ForeignKey(
        "muvis.MuvisBug",
        on_delete=models.PROTECT,
        null=False,
        blank=False)

    def __str__(self):
        return "Sample:{} Bug:{}".format(self.sample, self.bug.muvis_id)

    def sample_link(self):
        url = reverse('admin:samples_sample_change', args=[self.sample_id])
        return mark_safe('<a href={}>{}</a>'.format(url, self.sample))
    sample_link.short_description = "Sample"
    sample_link.admin_order_field = "sample"

    def muvis_link(self):
        url = reverse('admin:muvis_muvisbug_change', args=[self.bug.muvis_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, str(self.bug.title)))
    muvis_link.short_description = "Bug Title"
    muvis_link.admin_order_field = "title"

    def bugzilla_link(self):
        return self.bug.bugzilla_link()
    bugzilla_link.short_description = "Tracker link"
    bugzilla_link.admin_order_field = "bug"
