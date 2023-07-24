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
from .project import Project #pylint: disable=unused-import
from .contact import Contact #pylint: disable=unused-import
class ProjectOtherContacts(models.Model):
    """
        Create the intermediate model for the many to many so additional methods can be added
    """
    class Meta:
        db_table="projects_project_other_contacts"
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID")
    project = models.ForeignKey(
        "Project",
        on_delete=models.PROTECT)
    contact = models.ForeignKey(
        "Contact",
        on_delete=models.PROTECT)

    def project_name(self):
        return self.project.name

    def project_name_link(self):
        return self.project.name_link()

    def project_title(self):
        return self.project.full_title

    def principal_investigator(self):
        return self.project.pi

    def primary_contact(self):
        return self.project.contact

    def pi_link(self):
        return self.project.pi_link()
    pi_link.short_description = "Principal Investigator"

    def primary_contact_link(self):
        return self.project.contact_link()
    primary_contact_link.short_description = "Primary Contact"
