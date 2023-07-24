#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use, too-many-public-methods
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
from pathlib import Path
import sh

from django.db import models
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings


from private_storage.fields import PrivateFileField


from xrh_utils import convert_filesize, generate_qr_code

from .task_status import TASK_PENDING

class Project(models.Model):
    """
        Describes any project within the system.
        Must have a name, PI, & primary contact
    """
    class Meta:
        ordering = ["name", "pi"]

    def get_subfolder(self):
        return [self.pk]

    name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="A Short(ish) name for the project",
        unique=True,
        verbose_name="Project Name")
    full_title = models.CharField(
        max_length=255,
        db_index=True,
        help_text="The full title of the project",
        verbose_name="Project title",
        blank=True,
        null=True)
    description = models.TextField(
        blank=True,
        help_text="A longer form description of the project")
    url = models.URLField(
        blank=True,
        verbose_name="Project website",
        help_text="Link to the project website")
    team_liaison = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="The user who's acting as the main point of contact for the project")
    pi = models.ForeignKey(
        "Contact",
        on_delete=models.PROTECT,
        related_name="project_pi",
        help_text="The principle investigator on the project",
        verbose_name="Principal Investigator")
    contact = models.ForeignKey(
        "Contact",
        on_delete=models.PROTECT,
        related_name="project_contact",
        help_text="The main contact for the project (may be the PI)",
        verbose_name="Primary Contact")
    other_contacts = models.ManyToManyField(
        "Contact",
        blank=True,
        through="ProjectOtherContacts",
        related_name="project_contact_list",
        help_text="Other contacts for the project",
        verbose_name="Other Contacts")
    notes = models.TextField(
        blank=True,
        help_text="Additional notes")
    affiliation = models.ManyToManyField(
        "Institution",
        blank=True,
        help_text="Linked Organisations")
    funding = models.ManyToManyField(
        "Funder",
        blank=True,
        help_text="Sources of funding for the project")
    collaboration_agreement = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Memorandum of collaboration",
        help_text="Has a signed memorandum of collaboration been received?")
    status = models.ForeignKey(
        #Store the latest status in the db so that it can be easily filtered
        "ProjectStatus",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        editable=False) #Update automatically whenever an update is saved
    ethics_needed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Ethics approval needed",
        help_text="Does this project need ethics approval?")
    ethics_approved = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Ethics approval received",
        help_text="Has the ethics paperwork for this project been approved?")
    ethics_reference = models.TextField(
        blank=True,
        null=True,
        help_text="Any reference details for the ethics approval")
    mta_needed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Material Trasfer Agreement needed",
        help_text="Does this project need a Material Transfer Agreement (MTA)?")
    mta_approved = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="MTA received",
        help_text="Has the MTA paperwork for this project been approved?")
    mta_reference = models.TextField(
        blank=True,
        null=True,
        verbose_name="MTA Reference",
        help_text="Any reference details for the MTA")
    qr_code = PrivateFileField(
        "QR code",
        upload_to="project",
        upload_subfolder = get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    watch_list = models.ManyToManyField(
        get_user_model(),
        through="WatchList",
        related_name="watching",
        help_text="Users to email whenever there is a project update",
        blank=True)
    last_email_sent = models.DateField(
        blank=True,
        null=True,
        editable=False,
        help_text="When the last reminder email was sent out")


    def save(self, *args, **kwargs): #pylint: disable=signature-differs
        if self.ethics_needed and (self.ethics_approved is not True):
            #If ethics is needed and not explicitly approved then set it to false
            self.ethics_approved = False
        if self.mta_needed and (self.mta_approved is not True):
            #If MTA is needed and not explicitly set as approved then set to false
            self.mta_approved = False
        super().save(*args, **kwargs)
        self.add_qr_code()

    def pi_link(self):
        """
            Get a link to the PI admin page
        """
        url = reverse('admin:projects_contact_change', args=[self.pi_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.pi))
    pi_link.short_description = "Primary Investigator"
    pi_link.admin_order_field = "pi"

    def contact_link(self):
        """
            Get a link to the contact admin page
        """
        url = reverse('admin:projects_contact_change', args=[self.contact_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.contact))
    contact_link.short_description = "Primary Contact"
    contact_link.admin_order_field = "contact"

    def other_contact_links(self):
        """
            Show other contacts with links to all of them
        """
        contacts = self.other_contacts.all()
        output = ""
        no_contacts = len(contacts)
        for i in range(0, no_contacts):
            url = reverse('admin:projects_contact_change', args=[contacts[i].pk])
            output += '<a href="{}">{}</a>'.format(url, contacts[i].name)
            if i < (no_contacts - 1): # don't add new line after the last one
                output += "<br/>"
        return mark_safe(output)

    other_contact_links.short_description = "Other Contacts"

    def muvis_links(self):
        """
            Links to the associated muvis bugs
        """
        bugs = self.projectmuvismapping_set.all()
        output = ""
        no_bugs = len(bugs)
        for i in range(0, no_bugs):
            output += '<a href=https://muvis.soton.ac.uk/bugzilla/show_bug.cgi?id={}">{}</a>'.format( #pylint:disable=line-too-long
                bugs[i].muvis_id, str(bugs[i]))
        return mark_safe(output)
    muvis_links.short_description = "Muvis links"

    def affiliation_links(self):
        """
            Show linked institutions with links
        """
        institutes = self.affiliation.all()
        output = ""
        no_institutes = len(institutes)
        for i in range(0, no_institutes):
            url = reverse('admin:projects_institution_change', args=[institutes[i].pk])
            output += '<a href="{}">{}</a>'.format(url, institutes[i].name)
            if i < (no_institutes - 1):
                output += "<br/>"
        return mark_safe(output)
    affiliation_links.short_description = "Affiliation"

    def name_link(self):
        url = reverse('admin:projects_project_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.name))
    name_link.short_description = "Name"
    name_link.admin_order_field = "name"

    def str_link(self):
        url = reverse('admin:projects_project_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.__str__()))

    def project_id(self):
        return self.pk
    project_id.short_description = "ID"
    project_id.admin_order_field = "pk"

    def samples_in_custody(self):
        samples = self.sample_set.all()
        count = 0
        for sample in samples:
            if sample.our_custody():
                count += 1
        return count
    samples_in_custody.short_description = "Number of samples we have"

    def sample_count(self):
        return self.sample_set.count()
    sample_count.short_description = "Number of samples"

    def estimate_direct_scan_time(self):
        """
            Only counts scans for bugs associated with this project
        """
        time = timedelta(seconds=0)
        for buglink in self.projectmuvismapping_set.all():
            bug = buglink.muvis_id
            time += bug.estimate_total_scan_time()
        return time
    estimate_direct_scan_time.short_description = \
        "Estimation of the total scan time directly attributed to this project"

    def direct_scan_count(self):
        count = 0
        for buglink in self.projectmuvismapping_set.all():
            bug = buglink.muvis_id
            count += bug.no_scans()
        return count
    direct_scan_count.short_description = "Number of scans directly attributed to this project"

    def total_scan_count(self):
        count = 0
        for sample in self.sample_set.all():
            count += sample.no_scans()
        return count
    total_scan_count.short_description = "Number of scans for all associated samples"

    def average_scans_per_sample(self):
        return self.total_scan_count() / self.sample_count()
    average_scans_per_sample.short_description = \
        "Average number of scans for samples associated with the project"

    def estimate_average_scan_time_per_sample(self):
        return self.estimate_total_scan_time() / self.sample_count()
    estimate_average_scan_time_per_sample.short_description = \
        "Estimation of the average scan time for each sample"

    def direct_disk_usage_str(self):
        return convert_filesize(self.direct_disk_usage())

    def direct_disk_usage(self):
        dir_list = []
        for buglink in self.projectmuvismapping_set.all():
            dir_list += buglink.muvis_id.get_directories()
        if not dir_list:
            return 0
        dir_list_uniq = list(set(dir_list))
        try:
            return int(
                sh.du(*dir_list_uniq, "-sc").rstrip().split("\n")[-1:][0].split("\t")[0]
            ) * 1024
        except sh.ErrorReturnCode_1 as exp:
            logger = logging.getLogger("Disk usage")
            logger.error(str(exp))
            return None
    direct_disk_usage.short_description = "Disk used be scans directly attributed to this project"

    def total_disk_usage_str(self):
        return convert_filesize(self.total_disk_usage())

    def total_disk_usage(self):
        dir_list = []
        for sample in self.sample_set.all():
            dir_list += sample.get_directories()
        if not dir_list:
            return 0
        dir_list_uniq = list(set(dir_list))
        try:
            return int(
                sh.du(*dir_list_uniq, "-sc").rstrip().split("\n")[-1:][0].split("\t")[0]
            ) * 1024
        except sh.ErrorReturnCode_1 as exp:
            logger = logging.getLogger("Disk usage")
            logger.error(str(exp))
            return None
    total_disk_usage.short_description = "Total disk usage for all samples"

    def estimate_total_scan_time(self):
        """
            Scan time total for all samples associated with the project
        """
        time = timedelta(seconds=0)
        for sample in self.sample_set.all():
            time += sample.estimate_total_scan_time()
        return time
    estimate_total_scan_time.short_description = \
        "Estimation of total scan time for all associated samples"

    def report_count(self):
        return self.samplereport_set.count()
    report_count.short_description = "Number of reports generated"

    def xrhms_url(self):
        return "https://{}/ms/a/p/p/{}".format(
            settings.ALLOWED_HOSTS[0],
            self.pk)

    def add_qr_code(self, force=False):
        """
            Check to see if the QE code is already present, if not generate it and save it
            :param boolean force: Force regeneration of the code
        """
        if force or self.qr_code.name is None or self.qr_code.name == "":
            if force:
                self.qr_code.delete()
            #Check it isn't already in existance unless being force
            (temp_dir, fname) = generate_qr_code(self.xrhms_url())
            self.qr_code.save(fname, open(Path(temp_dir.name, fname), "rb"))
            self.save()

    def get_latest_update(self):
        return self.projectupdate_set.latest("last_updated")

    def has_pending_tasks(self):
        return self.projectupdate_set.filter(
            next_action_status=TASK_PENDING).exists()

    def has_overdue_tasks(self):
        return self.projectupdate_set.filter(
            next_action_status=TASK_PENDING,
            next_action_deadline__lt = now()).exists()

    def get_overdue_tasks(self):
        return self.projectupdate_set.filter(
            next_action_status=TASK_PENDING,
            next_action_deadline__lt = now())

    def notification_eligible(self):
        if not self.last_email_sent:
            return True
        interval_days = int(self.get_latest_update().status.notification_period * 7)
        if interval_days == 0:
            return False
        return (now().date() - self.last_email_sent).days > interval_days

    def inactive(self):
        update = self.get_latest_update()
        inactive_days = int(update.status.inactive_period * 7)
        if inactive_days == 0:
            return False
        return (now().date() - update.last_updated.date()).days > inactive_days

    def inactive_escalation(self):
        update = self.get_latest_update()
        inactive_days = int(update.status.escalation_period * 7)
        if inactive_days == 0:
            return False
        return (now().date() - update.last_updated.date()).days > inactive_days



    def __str__(self):
        """
            Override the default text representation"
        """
        return "{}-{}".format(self.name, self.pi)
