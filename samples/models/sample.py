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
from pathlib import Path
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError, models, transaction
from django.conf import settings
from django.utils.html import mark_safe
from django.urls import reverse


from private_storage.fields import PrivateFileField

from xrh_utils import generate_qr_code, generate_dm_code
from scans.models.dataset_status import DATASET_ONLINE
from .xrh_id import generate as xrh_id_generate
from .location import SampleLocationMapping
from .sample_type import SampleType #pylint: disable=unused-import

class Sample(models.Model):
    """
        Store all details about a sample
    """
    class Meta:
        unique_together = [
            ("xrh_id_number", "xrh_id_suffix", "sample_type")
        ]
    def get_subfolder(self):
        return [self.xrh_id()]


    original_id = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        verbose_name="Original ID",
        help_text="ID previously assigned to sample")
    xrh_id_prefix = models.ForeignKey(
        "SampleIdPrefix",
        on_delete=models.PROTECT,
        verbose_name="ID Prefix",
        blank=False,
        null=False,
        help_text="The prefix of the XRH ID field")
    xrh_id_number = models.IntegerField(
        blank=True,
        null=False,
        db_index=True,
        editable=False,
        verbose_name="XRH ID Number",
        help_text="The numeric part of the ID without the checksum")
    xrh_id_suffix = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        editable=False,
        verbose_name="ID Suffix",
        help_text="The suffix part of the ID")
    parent_process = models.ForeignKey(
        "Process",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="parent",
        help_text="The process by which the sample was created (if known)")
    description = models.TextField(
        blank=True,
        help_text="Long form description of the sample")
    date_entered = models.DateTimeField(
        auto_now_add=True)
    project = models.ManyToManyField(
        "projects.Project",
        db_index=True,
        help_text="Projects to which this sample is associated")
    bug = models.ManyToManyField(
        "muvis.MuvisBug",
        through = "SampleMuvisMapping")
    location = models.ManyToManyField(
        "Location",
        through="SampleLocationMapping")
    sample_type = models.ForeignKey(
        "SampleType",
        on_delete=models.PROTECT,
        verbose_name="Type",
        db_index=True,
        help_text="The type of the sample. Once created this CANNOT be easily changed.")
    tissue = models.ForeignKey(
        "Tissue",
        db_index=True,
        on_delete=models.PROTECT,
        help_text="The tissue that the sample is of. Once created this CANNOT be easily changed.")
    species = models.ForeignKey(
        "Species",
        db_index=True,
        on_delete=models.PROTECT,
        help_text="What species is the sample from. Once created this CANNOT be easily changed.")
    storage_requirement = models.ForeignKey(
        "StorageRequirement",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        db_index=True,
        help_text="Any spefic requirements about how the item is stored")
    condition = models.ForeignKey(
        "Condition",
        on_delete=models.PROTECT,
        db_index=True,
        help_text="Any known details about the condition of the sample",
        null=True,
        blank=True)
    qr_code = PrivateFileField(
        "QR code",
        upload_to="sample",
        upload_subfolder = get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    dm200_code = PrivateFileField(
        "DM200 code",
        upload_to="sample",
        upload_subfolder = get_subfolder,
        content_types=["image/png"],
        max_file_size=settings.ATTACHMENT_FILE_SIZE_LIMIT,
        blank=True,
        null=True)
    full_xrh_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        editable=False, # For use internally for searching only
        help_text="Used to enable searching by full ID")
    extraction_method = models.ForeignKey(
        "ExtractionMethod",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Extraction Method / Surgical Procedure",
        help_text="How the tissue was extracted")

    def xrh_id(self):
        """
            Compile the ID and the check digit into the required form
        """
        if self.xrh_id_suffix is None:
            suffix = self.sample_type.suffix
        else:
            #Only use the number if it's set
            suffix = self.xrh_id_suffix
        return xrh_id_generate(str(self.xrh_id_prefix), str(self.xrh_id_number), suffix)
    xrh_id.short_description = "XRH ID"
    xrh_id.admin_order_field = "full_xrh_id"
    def url(self):
        """
            Get the URL for the sample
            :return the URL
        """
        return "https://{}/ms/a/sa/sa/{}".format(
            settings.ALLOWED_HOSTS[0],
            self.pk)

    def xrh_id_link(self):
        url = reverse('admin:samples_sample_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.xrh_id()))
    xrh_id_link.short_description = "XRH ID"
    xrh_id.admin_order_field = "full_xrh_id"

    def species_link(self):
        """
            Return a species description complete with link to the species
        """
        url = reverse('admin:samples_species_change', args=[self.species_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.species))
    species_link.short_description = "Species"
    species_link.admin_order_field = "species"


    def extraction_method_link(self):
        url = reverse('admin:samples_extractionmethod_change', args=[self.extraction_method_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.extraction_method))
    extraction_method_link.short_description = "Extraction Method / Surgical Procedure"
    extraction_method_link.order_field = "extraction_method"

    def sample_type_link(self):
        """
            Return the sample type with a link to the admin page for the type
        """
        url = reverse('admin:samples_sampletype_change', args=[self.sample_type_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.sample_type))
    sample_type_link.short_description = "Sample Type"
    sample_type_link.admin_order_field = "sample_type"

    def tissue_link(self):
        """
            Return a link to the tissue type
        """
        url = reverse('admin:samples_tissue_change', args=[self.tissue_id])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.tissue))
    tissue_link.short_description = "Tissue"
    tissue_link.admin_order_field = "tissue"

    def condition_link(self):
        """
            Return a link to the condition page
        """
        status = self.condition
        if status is None:
            return "-"
        url = reverse('admin:samples_condition_change', args=[status.pk]) #pylint:disable=no-member
        return mark_safe('<a href="{}">{}</a>'.format(url, status))
    condition_link.short_description = "Condition"
    condition_link.admin_order_field = "condition"

    def storage_requirement_link(self):
        """
            Return a link to the storage requirement page
        """
        requirement = self.storage_requirement
        if requirement is None:
            return "-"
        url = reverse('admin:samples_storagerequirement_change', args=[requirement.pk]) #pylint:disable=no-member
        return mark_safe('<a href="{}">{}</a>'.format(url, requirement))
    storage_requirement_link.short_description = "Storage Requirement"
    storage_requirement_link.admin_order_field = "storage_requirement"

    def current_location(self):
        """
            Get the current storage location for the sample
        """
        return SampleLocationMapping.objects.filter(sample=self).latest("date_entered").location
    current_location.short_description = "Current Location / Status"

    def our_custody(self):
        """
            Get a boolean defining if the sample is in our custody or not
        """
        try:
            return self.current_location().our_control
        except ObjectDoesNotExist:
            return False


    def current_location_link(self):
        """
            Generate a link to the current location page
        """
        location = self.current_location()
        url = reverse('admin:samples_location_change', args=[location.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, location.name))
    current_location_link.short_description = "Current Location / Status"

    def additional_risks(self):
        """
            Is this sample subject to an additional Risk Assement
        """
        try:
            if self.sample_type.additional_risks:
                return "Yes - See Risk Assessment for Sample Type"
            return "No"
        except ObjectDoesNotExist:
            return "-"

    def __str__(self):
        """
            Just use the sample name as the string representation
        """
        return self.xrh_id()

    def save(self, *args, **kwargs): #pylint:disable=signature-differs
        """
            Overwrite the save method so that various bits can be done automatically
        """
        if not self.pk: #If pk is null then it's the creation of the object
            if not self.xrh_id_number:
                #If it's already got an ID number (for example by processing don't overwrite
                try:
                    with transaction.atomic():
                        latest = Sample.objects.select_for_update().latest("xrh_id_number")
                        # Lock the latest ID number
                        new_id = latest.xrh_id_number + 1
                        self.xrh_id_number = new_id
                        super().save(*args, **kwargs) #Actually create the object
                except ObjectDoesNotExist:
                    #Trying to insert first record into database
                    with transaction.atomic():
                        no_samples = Sample.objects.count()
                        if no_samples != 0:
                            raise DataError( #pylint: disable=raise-missing-from
                                "Error handling insertion of first sample, please try again")
                        new_id = 1
                        self.xrh_id_number = new_id
                        super().save(*args, **kwargs) #Actually create the object
                self.save()
            self.add_qr_code()
            self.add_dm200_code()
            if not self.full_xrh_id:
                self.full_xrh_id = self.xrh_id()
                self.save()
        super().save(*args, **kwargs) #Otherwise just save the object

    def project_links(self):
        """
            Produced a list of links to the project for the sample
            Each project listed on a new line
        """
        projects = self.project.all()
        output = ""
        no_projects = len(projects)
        for i in range(0, no_projects):
            url = reverse('admin:projects_project_change', args=[projects[i].pk])
            output += '<a href="{}">{}</a>'.format(url, str(projects[i]))
            if i < (no_projects - 1):
                output += "<br/>"
        return mark_safe(output)
    project_links.short_description = "Projects"

    def add_qr_code(self, force=False):
        """
            Check to see if the QE code is already present, if not generate it and save it
            :param boolean force: Force regeneration of the code
        """
        if force or self.qr_code.name is None or self.qr_code.name == "":
            if force:
                self.qr_code.delete()
            #Check it isn't already in existance unless being force
            (temp_dir, fname) = generate_qr_code(self.url())
            self.qr_code.save(fname, open(Path(temp_dir.name, fname), "rb"))
            self.save()

    def add_dm200_code(self, force=False):
        """
            Check to see if the DM200 code is already present, if not generate and save it
            :param boolean force: Force overwritten of existing one
        """
        if force or self.dm200_code.name is None or self.dm200_code.name == "":
            if force:
                self.dm200_code.delete()
            (temp_dir, fname) = generate_dm_code(self.url())
            self.dm200_code.save(fname, open(Path(temp_dir.name, fname), "rb"))

    def no_scans(self):
        return self.scan_set.count()
    no_scans.short_description = "Number of times scanned"

    def estimate_total_scan_time(self):
        time = timedelta(seconds=0)
        for scan in self.scan_set.all():
            scan_time = scan.estimate_time()
            if scan_time:
                time += scan_time
        return time
    estimate_total_scan_time.short_description = "Estimate total length of scans"

    def get_directories(self):
        dir_list = []
        for scan in self.scan_set.all():
            if scan.dataset_status == DATASET_ONLINE:
                dir_list.append(scan.get_directory())
        return dir_list

    def is_confidential(self):
        return self.xrh_id_prefix == SampleIdPrefix.objects.get(prefix="CMCF")



class SampleIdPrefix(models.Model):
    """
        Prefixes that can be used for sample IDs
    """
    prefix = models.CharField(
        max_length=4,
        unique=True,
        db_index=True,
        help_text="The characters that are available for use as sample prefixes")
    description = models.TextField(
        blank=True,
        help_text="What the short code is used for")

    class Meta:
        """
            Fix the plural
        """
        verbose_name_plural = "Sample ID prefixes"
        verbose_name = "Sample ID prefix"
    def __str__(self):
        """
            Just use the sample name as the string representation
        """
        return self.prefix
