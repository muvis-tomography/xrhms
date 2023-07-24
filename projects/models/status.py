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
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

import email_processor
from .task_status import TASK_STATUS_CHOICES, TASK_PENDING, TASK_COMPLETE
from .project import Project #pylint: disable=unused-import

class ProjectStatus(models.Model):
    """
        A status that a project can be assigned whenever an update is added
    """
    class Meta:
        verbose_name_plural = "Statuses"
    name = models.CharField(
        max_length=50,
        db_index=True,
        unique=True,
        help_text="Name of status")
    description = models.TextField(
        blank=True,
        help_text="Description of status")
    inactive_period = models.FloatField(
        default=0,
        blank=False,
        null=False,
        help_text="How long to wait before sending the first inactive email (weeks)")
    notification_period = models.FloatField(
        default=0,
        blank=False,
        null=False,
        help_text="How long to wait between sending reminders (weeks)")
    escalation_period = models.FloatField(
        default=0,
        blank=False,
        null=False,
        help_text="How long to wait before esclating the inactive reminder (weeks)")

    def __str__(self):
        return self.name

class ProjectUpdate(models.Model):
    project = models.ForeignKey(
        "Project",
        on_delete=models.PROTECT,
        db_index=True,
        blank=False,
        null=False,
        help_text="Project the update relates to")
    status = models.ForeignKey(
        "ProjectStatus",
        on_delete=models.PROTECT,
        db_index=True,
        blank=True,
        null=False,
        help_text="Current status of the project")
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name="By",
        blank=True,
        help_text="The user who made the change")
    last_updated = models.DateTimeField(
        db_index = True,
        verbose_name="Last Updated",
        auto_now_add=True)
    last_action_date = models.DateField(
        db_index = True,
        blank=True,
        null=True,
        verbose_name="Last Action (Date)")
    last_action = models.TextField(
        blank=True,
        null=True,
        verbose_name="Details of Last Action")
    notes = models.TextField(
        blank=True,
        null=True)
    next_action = models.TextField(
        blank=True,
        null=True)
    next_action_deadline = models.DateField(
        db_index=True,
        blank=True,
        null=True)
    next_action_status_updated_date = models.DateTimeField(
        blank=True,
        null=True,
        editable=False)
    next_action_status = models.CharField(
        max_length=2,
        choices=TASK_STATUS_CHOICES,
        blank=False,
        null=False,
        default=TASK_PENDING)

    def clean(self):
        if not hasattr(self, "status"):
            if self.project.status:
                self.status = self.project.status
            else:
                self.status = ProjectStatus.objects.get(name="Active")
        if self.next_action is None or self.next_action == "":
            self.next_action_status = TASK_COMPLETE
        if self.pk is None and self.status.notification_period == 0:
            #check pk is none to avoid validating existing entries
            if self.project.has_pending_tasks():
                raise ValidationError(
                    _("Cannot set this status for a project that still has pending tasks"))

    def save(self, *args, **kwargs): #pylint: disable=signature-differs
        new_item = self.pk is None
        self.next_action_status_updated_date = now()
        super().save(*args, **kwargs) # save the object
        if new_item:
            self.project.status = self.status
            self.project.save()

    def send_update_emails(self):
        emailer = email_processor.EmailProcessor()
        return emailer.send_watch_list_emails(self, exclude=[self.user])

    def project_link(self):
        return self.project.name_link()
    project_link.short_description = "Project Link"
    project_link.admin_sort_order = "project"

    def __str__(self):
        return "{}-{}".format(self.project, self.last_updated)
