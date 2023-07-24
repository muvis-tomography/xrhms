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

    Custom forms used for the admin interface
"""
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.db.models.expressions import RawSQL

from .models import SampleLocationMapping
from .models import ProcessType
from .models import Sample

SAMPLE_TYPE_SUFFIX_MIN_LENGTH = 4
SAMPLE_TYPE_SUFFIX_MAX_LENGTH = 6
import logging
class SampleIdPrefixForm(forms.ModelForm):
#    prefix = forms.CharField(max_length=4)
#    description = forms.CharField()

    def clean_prefix(self):
        error_list = []
        data = self.cleaned_data["prefix"]
        if not data.isalpha():
            error_list.append(ValidationError(_('Invalid prefix - must be letters only')))
        if  len(data) != 4:
            error_list.append(ValidationError(_('Invalid prefix - must be 4 letters long')))
        if len(error_list) != 0:
            raise ValidationError(error_list)
        return data.upper()

class LocationSampleInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(LocationSampleInlineFormSet, self).__init__(*args, **kwargs)
        self.queryset = SampleLocationMapping.objects.filter(id__in=RawSQL('SELECT id FROM samples_samplelocationmapping AS slm1, (SELECT sample_id, MAX(date_entered) AS last_move FROM samples_samplelocationmapping GROUP BY sample_id) AS slm2 WHERE slm1.sample_id = slm2.sample_id AND slm1.date_entered = slm2.last_move AND location_id =%s', (self.instance.pk,)))

class ProcessForm(forms.ModelForm):
    def clean_sample(self):
        try:
            sample = self.cleaned_data["sample"]
        except KeyError:
            raise ValidationError(_("Must specify a sample"))
        return sample

    
    def clean(self):
        sectioning_required_fields = ["start_slice", "number_of_slices", "block_left"]
        try:
            process = self.cleaned_data["process"]
        except KeyError:
            raise ValidationError(_("Must specify which process is being performed"))
        sample = self.cleaned_data["sample"]
        if hasattr(sample, "process"):
            raise ValidationError(_("Sample has already been processed"))
        if process  == ProcessType.objects.get(name="Sectioning"):
            try:
                for field in sectioning_required_fields:
                    if self.cleaned_data[field] is None:
                        self.add_error(field, ValidationError(
                            _("If performing a sectioning operation then the {} must be filled in").format(field)))
            except KeyError:
                pass #IF can't find the key then it's already failed validation elsewhere
            start_slice = self.cleaned_data["start_slice"]
            if Sample.objects.filter(
                    xrh_id_number=sample.xrh_id_number,
                    xrh_id_suffix="{:03d}".format(start_slice)).exists():
                self.add_error("start_slice", ValidationError(
                    _("That slice number already exists for that sample")))
        else:
            for field in sectioning_required_fields:
                if self.cleaned_data[field] is not None:
                    self.add_error(field, ValidationError(
                        _("If not performing a sectioning operation then the {} must be not filled in").format(field)))
        return self.cleaned_data

class SampleTypeForm(forms.ModelForm):
    def clean_suffix(self):
        data = self.cleaned_data["suffix"]
        min_length = SAMPLE_TYPE_SUFFIX_MIN_LENGTH
        max_length = SAMPLE_TYPE_SUFFIX_MAX_LENGTH
        if len(data) < min_length:
            self.add_error("suffix", ValidationError(
                _("The suffix must be at least {} characters long. ({} max)".format(min_length, max_length))))
        elif len(data) > max_length:
            self.add_error("suffix", ValidationError(
                _("The suffix must be at most {} characters long. ({} min)".format(max_length, min_length))))
        return data.upper()

class SampleReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SampleReportForm, self).__init__(*args, **kwargs)
        try:
            sample = self.initial["sample"]
            self.fields["project"].queryset = Sample.objects.get(pk=sample).project.all()
        except KeyError:
            pass

    def clean(self):
        sample  = self.cleaned_data["sample"]
        try:
            project = self.cleaned_data["project"]
            if project not in sample.project.all():
                self.add_error("project", ValidationError(_(
                    "Project is not linked to Sample")))
                logger = logging.getLogger("SampleReport")
                logger.error("Project %s not in samples (%s)[%d] list", project, sample, sample.pk)
        except KeyError:
            pass
        return self.cleaned_data
#https://stackoverflow.com/a/1233644/535237
class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form
