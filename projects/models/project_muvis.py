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


class ProjectMuvisMapping(models.Model):
    project = models.ForeignKey(
        "Project",
        on_delete=models.PROTECT,
        null=False,
        blank=False)
    muvis_id = models.ForeignKey(
        "muvis.MuvisBug",
        on_delete=models.PROTECT,
        null=False,
        blank=False)

    def __str__(self):
        return "Project:{} Bug:{}".format(self.project_id, self.muvis_id.muvis_id)

    def project_link(self):
        url = reverse('admin:projects_project_change', args=[self.project_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.project))
    project_link.short_description = "Project"
    project_link.admin_order_field = "project"

    def muvis_link(self):
        url = reverse('admin:muvis_muvisbug_change', args=[self.muvis_id.muvis_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, str(self.muvis_id.title)))
    muvis_link.short_description = "Bug Title"
    muvis_link.admin_order_field = "title"

    def bugzilla_link(self):
        return self.muvis_id.bugzilla_link()
    bugzilla_link.short_description = "Tracker link"
    bugzilla_link.admin_order_field = "muvis_id"
