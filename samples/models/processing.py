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
from django.db import transaction

from django.contrib.auth import get_user_model

from django.utils import timezone
from django.utils.html import mark_safe

from django.urls import reverse

from .location import Location, SampleLocationMapping

from .sample import Sample


class Process(models.Model):
    class Meta:
        verbose_name_plural = "Processes"
    sample = models.OneToOneField(
        "Sample",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="The sample that was used in the process")
    process = models.ForeignKey(
        "ProcessType",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="The process carried out on the sample")
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="The user who carried out the process")
    date = models.DateTimeField(
        db_index=True,
        default=timezone.now,
        blank=False,
        null=False,
        help_text="When was the process carried out")
    start_slice = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Start slide",
        help_text="The number of the first slide created")
    number_of_slices = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Number of slides",
        help_text="The number of slides created")
    block_left = models.BooleanField(
        blank=True,
        null=True,
        help_text="Is there any block left intact after sectioning?")
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any notes about the processing")

    def process_link(self):
        url = reverse('admin:samples_process_change', args=[self.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, self.process))
    process_link.short_description = "Process"
    process_link.admin_order_field = "process"

    def __str__(self):
        return "{}-{}".format(self.sample, self.process)

    def save(self, *args, **kwargs): #pylint:disable=signature-differs
        pk = self.pk #pylint:disable=invalid-name
        super().save(*args, **kwargs) #Save the object
        if not pk: #This is the first saving of an object
            sample = self.sample
            user = self.user
            date = self.date
            notes = self.notes
            process = self.process
            projects = self.sample.project.all()
            sample_type = process.new_type
            with transaction.atomic():
                #Mark parent sample as processed
                slm = SampleLocationMapping(
                    sample=sample,
                    location = Location.objects.get(name="Processed"),
                    date_entered=date,
                    user=user,
                    notes=notes
                )
                slm.save()
                #If slicing create required new samples
                if process == ProcessType.objects.get(name="Sectioning"):
                    start_no = self.start_slice
                    slice_count = self.number_of_slices
                    end_no = start_no + slice_count
                    for slide in range(start_no, end_no):
                        xrh_id_suffix = "{:03d}".format(slide)
                        sam = Sample(
                            original_id=sample.original_id,
                            xrh_id_prefix=sample.xrh_id_prefix,
                            xrh_id_number=sample.xrh_id_number,
                            xrh_id_suffix=xrh_id_suffix,
                            parent_process=self,
                            date_entered=date,
                            sample_type=sample_type,
                            tissue=sample.tissue,
                            species=sample.species,
                            condition=sample.condition,
                            extraction_method=sample.extraction_method,
                        )
                        sam.save()
                        for proj in projects: #iterate through project list & add them to new sample
                            sam.project.add(proj)
                        sam.save()
                    if self.block_left: # There's a chunk of block left so create sample record for that #pylint: disable=line-too-long
                        #work out the new suffix for the block
                        if sample.xrh_id_suffix is None:
                            xrh_id_suffix = "A"
                        elif sample.xrh_id_suffix == "Z":
                            raise ValueError(
                                "Unable to slice this block any further and not use it all")
                        else:
                            xrh_id_suffix = chr(ord(sample.xrh_id_suffix) + 1)
                            #convert to int then increment and back to char
                        sam = Sample(
                            original_id=sample.original_id,
                            xrh_id_prefix=sample.xrh_id_prefix,
                            xrh_id_number=sample.xrh_id_number,
                            xrh_id_suffix=xrh_id_suffix,
                            parent_process=self,
                            date_entered=date,
                            sample_type=sample.sample_type,
                            tissue=sample.tissue,
                            species=sample.species,
                            condition=sample.condition,
                            extraction_method=sample.extraction_method,
                        )
                        sam.save()
                        for proj in projects: #iterate through project list & add to new sample
                            sam.project.add(proj)
                        sam.save()
                else:
                    sam = Sample(
                            original_id=sample.original_id,
                            xrh_id_prefix=sample.xrh_id_prefix,
                            xrh_id_number=sample.xrh_id_number,
                            parent_process=self,
                            date_entered=date,
                            sample_type=sample_type,
                            tissue=sample.tissue,
                            species=sample.species,
                            condition=sample.condition,
                            extraction_method=sample.extraction_method,
                    )
                    sam.save()
                    for proj in projects:   #iterate through project list and add them to new sample
                        sam.project.add(proj)
                        sam.save()

class ProcessType(models.Model):
    """
        Description of the process type eg. freeze, wax embed formalin etc.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The name of the process")
    description = models.TextField(
        blank=True,
        help_text="A description of the process")
    new_type = models.ForeignKey(
        "SampleType",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="The type of sample created when process is applied")

    def __str__(self):
        return self.name

class Stain(models.Model):
    """
        Any staining chemical that may be used on a sample
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The name of the stain")
    description = models.TextField(
        blank=True,
        help_text="Description of the Chemical")

    def __str__(self):
        return self.name
