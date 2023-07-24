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
from django.contrib import admin, messages
from django.contrib.auth import get_user
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
#from django.utils import timezone
from django.shortcuts import render
from django.utils.html import mark_safe

from projects.models import Project
from scans.models import Scan
from muvis.models import MuvisBug
from labels.utils import print_sample_label, LA62_PRINTER_11354, LB68_PRINTER_11354
from xrh_utils import create_report_bundle
from deleting_file_wrapper import DeletingFileWrapper

from .forms import (
    LocationSampleInlineFormSet,
    ProcessForm,
    RequiredInlineFormSet,
    SampleIdPrefixForm,
    SampleReportForm,
    SampleTypeForm)

from .models import (
    Condition,
    ExtractionMethod,
    Location,
    Process,
    ProcessType,
    Sample,
    SampleAttachment,
    SampleAttachmentType,
    SampleIdPrefix,
    SampleLocationMapping,
    SampleMuvisMapping,
    SampleReport,
    SampleType,
    SampleTypeAttachment,
    Species,
    StorageRequirement,
    ReportScanMapping,
    Tissue,
    Stain)
from .views import sample_details_csv

#from .reports import generate_report
# Register your models here.

class SampleScanInline(admin.TabularInline):
    model = Scan
    readonly_fields = ["name_link", "dataset_status", "scan_type"]
    fields = ["name_link", "scan_date", "operator", "dataset_status", "scan_type", "sample"]
    ordering = ["-scan_date"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SampleLocationInline(admin.TabularInline):
    model = SampleLocationMapping
    formset = LocationSampleInlineFormSet
    verbose_name = "Sample"
    verbose_name_plural = "Samples"
    extra = 0
    can_delete = False
    readonly_fields = ["species", "tissue", "notes"]
    exclude = ["user"]

    def species(self, instance):
        return instance.sample.species

    def tissue(self, instance):
        return instance.sample.tissue

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    verbose_name = "Sample Location / Status"
    verbose_name_plural = "Sample Locationss / Statuses"
    list_display = ["name", "location", "our_control", "description"]
    list_filter = ["our_control"]
    inlines = [
        SampleLocationInline
    ]

class ChildInline(admin.TabularInline):
    verbose_name = "Sample Processing Applied"
    verbose_name_plural = "Sample Processing Applied"
    model = Process
    extra = 0
    can_delete = False
    readonly_fields = ["process_link", "user", "date", "notes"]
    fields = ["process_link", "user", "date", "notes"]

    def has_add_permission(self, request, obj=None):
        return False

class LocationInline(admin.TabularInline):
    verbose_name = "Sample Location / Status"
    verbose_name_plural = "Sample Location / Status History"
    model = SampleLocationMapping
    extra = 0
    can_delete = False
    ordering = ["date_entered"]
    list_display = ["location", "user"]
    readonly_fields = ["date_entered"]
    fields = ["location", "user", "date_entered", "notes"]

class MuvisBugLinkInline(admin.TabularInline):
    verbose_name = "Related Muvis bug"
    verbose_name_plural = "Related Muvis bugs"
    model=SampleMuvisMapping
    list_select_related = True
    max_rows = 0
    extra = 0
    fields = ["bugzilla_link", "muvis_link", "status", "resolution"]
    readonly_fields = ["muvis_link", "status", "resolution", "bugzilla_link"]

    def title(self, instance):
        return instance.bug.title

    def status(self, instance):
        return instance.bug.status
    status.short_description = "Status"

    def resolution(self, instance):
        return instance.bug.resolution
    resolution.short_description = "Resolution"

    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class MuvisBugAddInline(admin.StackedInline):
    verbose_name = "Related Muvis bug"
    verbose_name_plural = "Related Muvis bugs"
    model=SampleMuvisMapping
    max_rows = 1
    extra = 1
    autocomplete_fields = ["bug"]
    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

class SampleAttachmentInline(admin.TabularInline):
    model=SampleAttachment
    max_rows = 0
    extra = 0
    readonly_fields = ["name_link", "attachment_type", "notes", "uploaded"]
    fields = ["name_link", "attachment_type", "uploaded", "notes"]
    def has_add_permission(self, request, obj=None):
        return False

class SampleAttachmentAddInline(admin.StackedInline):
    verbose_name = "Add Sample Attachment"
    model=SampleAttachment
    max_rows = 0
    extra = 0
    fields = ["name", "attachment_type", "attachment", "notes"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

class SampleReportInline(admin.TabularInline):
    model = SampleReport
    classes = ["collapse"]
    max_rows = 0
    extra = 0
    ordering = ["-date_generated"]
    readonly_fields = [
        "date_generated_link", "count_video_types",
    ]
    fields = [
        "project", "date_generated_link", "count_video_types",
        "generated_by", "generation_success"
    ]

    def count_video_types(self, instance):
        return instance.count_video_types()
    count_video_types.short_description = "No. of video types"

    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    """
        Override the default admin options for samples
    """
    search_fields = ["full_xrh_id", "original_id", "project__name"]
    ordering = ["-date_entered", "xrh_id_prefix", "xrh_id_number", "xrh_id_suffix"]
    list_display = (
        "xrh_id", "original_id", "project_links", "sample_type_link", "species_link", "tissue_link",
        "current_location_link", "date_entered")
    order_by = ["xrh_id_prefix", "xrh_id_number", "xrh_id_suffix"]
    list_filter = ["sample_type", "species", "tissue", "extraction_method", "project__name"]
    fieldsets = [
        ("Identification", {"fields": [
            "xrh_id_prefix", "xrh_id", "original_id", "project",
            ("qr_code_img", "dm200_code_img")
        ]}),
        ("Details", {"fields": [
            "description", "sample_type", "additional_risks", "species",
            "tissue", "condition", "extraction_method", "storage_requirement"]}),
        ("Imaging", {"fields": [
            "no_scans", "estimate_total_scan_time"]}),
    ]
    autocomplete_fields = [
        "xrh_id_prefix", "project", "sample_type", "species", "tissue",
        "condition", "storage_requirement", "extraction_method"]
    inlines = [
        MuvisBugLinkInline,
        MuvisBugAddInline,
        LocationInline,
        ChildInline,
        SampleScanInline,
        SampleAttachmentInline,
        SampleAttachmentAddInline,
        SampleReportInline
    ]
    actions = [
        "bulk_move",
        "bulk_print_la62",
        "bulk_print_lb68",
        "bulk_proj_add",
        "generate_csv",
        "view_details",
        "bulk_bug_add",
    ]

    def bulk_bug_add(self, request, queryset):
        if 'apply' in request.POST:
            bug_obj = MuvisBug.objects.get(pk=request.POST.get("bug"))
            for sample in queryset:
                smm = SampleMuvisMapping()
                smm.sample = sample
                smm.bug = bug_obj
                smm.save()
            messages.info(request, "Bug {} added to {} samples".format(
                bug_obj.muvis_id, len(queryset)))
            return HttpResponseRedirect(request.get_full_path())
        if 'abort' in request.POST:
            messages.info(request, "Muvis bug add aborted")
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["opts"] = Sample._meta
        context["is_popup"] = False
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        context["autocomplete_url"] = reverse('admin:muvis_muvisbug_autocomplete')
        context["samples"] = []
        for sample in queryset:
            details = {}
            details["pk"] = sample.pk
            details["xrh_id"] = sample.full_xrh_id
            details["original_id"] = sample.original_id
            context["samples"].append(details)
        return render(request, "admin/samples/sample_bug_add.html", context=context)

    bulk_bug_add.short_description = "Bulk add muvis bug"

    def view_details(self, request, queryset):
        context = {}
        context["opts"] = Sample._meta
        context["is_popup"] = False
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        context["samples"] = []
        for sample in queryset:
            details = {}
            details["xrh_id"] = sample.full_xrh_id
            if sample.original_id:
                details["original_id"] = sample.original_id
            else:
                details["original_id"] = "-"
            context["samples"].append(details)
        return render(request, "admin/samples/sample_list.html", context=context)
    view_details.short_description = "View basic details"

    def generate_csv(self, request, queryset):
        return sample_details_csv(queryset)
    generate_csv.short_description = "Generate CSV dump"


    def bulk_proj_add(self, request, queryset):
        if 'apply' in request.POST:
            project_obj = Project.objects.get(pk=request.POST.get("project", ))
            for sample in queryset:
                sample.project.add(project_obj)
            messages.success(request, "Added project to {} samples".format(len(queryset)))
            return HttpResponseRedirect(request.get_full_path())
        if 'abort' in request.POST:
            messages.info(request, "Project add aborted")
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["opts"] = Sample._meta
        context["is_popup"] = False
        context["samples"] = queryset
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        projects = []
        project_set = Project.objects.all()
        for project_obj in project_set:
            project = {}
            project["pk"] = project_obj.pk
            project["name"] = str(project_obj)
            projects.append(project)
        context["projects"] = projects
        return render(request,
            "admin/samples/bulk_proj_add.html",
            context=context)
    bulk_proj_add.short_description = "Add additional project"



    def bulk_move(self, request, queryset):
        if 'apply' in request.POST:
            location_obj = Location.objects.get(pk=request.POST.get("location", ))
            for sample in queryset:
                slm = SampleLocationMapping()
                slm.sample = sample
                slm.location = location_obj
                slm.user = request.user
                slm.notes = "Bulk move:\n" + request.POST.get("notes", )
                slm.save()

            messages.success(request, "Moved {} samples".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())
        if 'abort' in request.POST:
            messages.info(request, "Move aborted")
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["opts"] = Sample._meta
        context["is_popup"] = False
        context["samples"] = queryset
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        location_set = Location.objects.all()
        locations = []
        for location_obj in location_set:
            location = {}
            location["pk"] = location_obj.pk
            location["name"] = location_obj.name
            locations.append(location)
        context["locations"] = locations
        return render(request,
            "admin/samples/bulk_move.html",
            context=context)
    bulk_move.short_description = "Move selected samples"

    def bulk_print_lb68(self, request, queryset):
        self.bulk_print(request, queryset, LB68_PRINTER_11354)
    bulk_print_lb68.short_description = "Print labels (LB68)"

    def bulk_print_la62(self, request, queryset):
        self.bulk_print(request, queryset, LA62_PRINTER_11354)
    bulk_print_la62.short_description = "Print labels (LA62)"

    def bulk_print(self, request, queryset, printer):
        success = True
        for sample in queryset:
            success &= print_sample_label(sample, printer_name=printer)
        if success:
            messages.success(request, "Label(s) sent for printing.")
        else:
            messages.error(request, "Failed to send label(s) for printing.")

    def get_readonly_fields(self, request, obj=None):
        """
            Fields that should be editable at create but not after
        """
        always = [
            "xrh_id", "qr_code_img", "dm200_code_img", "additional_risks", "no_scans",
            "estimate_total_scan_time"
        ]
        if obj:
            return always + [
                "xrh_id_prefix", "parent_process", "sample_type",
                "tissue", "species"
            ]
        return always

    def response_change(self, request, obj):
        if "_process" in request.POST:
            return HttpResponseRedirect(
                reverse('admin:samples_process_add') + "?sample={}&user={}".format(
                    obj.pk, get_user(request).id))
        printer = None
        if "_print_label_la62" in request.POST:
            printer = LA62_PRINTER_11354
        if "_print_label_lb68" in request.POST:
            printer = LB68_PRINTER_11354
        if printer:
            if print_sample_label(obj, printer_name=printer):
                messages.success(request, "Label sent for printing.")
            else:
                messages.error(request, "Failed to send label for printing.")
            return HttpResponseRedirect(reverse('admin:samples_sample_change', args=[obj.id]))
        if "_report" in request.POST:
            return HttpResponseRedirect(reverse(
                "admin:samples_samplereport_add") + "?sample={}".format(obj.pk))
        if "_duplicate" in request.POST:
            params = {}
            params["xrh_id_prefix"] = obj.xrh_id_prefix.pk
            if obj.sample_type:
                params["sample_type"] = obj.sample_type.pk
            if obj.tissue:
                params["tissue"] = obj.tissue.pk
            if obj.species:
                params["species"] = obj.species.pk
            if obj.storage_requirement:
                params["storage_requirement"] = obj.storage_requirement.pk
            if obj.condition:
                params["condition"] = obj.condition.pk
            if obj.extraction_method:
                params["extraction_method"] = obj.extraction_method_id
            params["project"] = ",".join(
                str(proj) for proj in obj.project.all().values_list("pk", flat=True))
            data_str = "?"
            for key, value in params.items():
                data_str += "%s=%s&" %(key, str(value))
            return HttpResponseRedirect(reverse("admin:samples_sample_add") + data_str)
        return super().response_change(request, obj)

    def qr_code_img(self, instance):
        return mark_safe('<img src="{}"/>'.format(instance.qr_code.url))
    qr_code_img.short_description = "QR code"

    def dm200_code_img(self, instance):
        return mark_safe('<img src="{}"/>'.format(instance.dm200_code.url))
    dm200_code_img.short_description = "DM200 code"

    def save_formset(self, request, form, formset, change):
        if formset.model == SampleLocationMapping:
            instances = formset.save(commit=False)
            for instance in instances:
                try:
                    #Despite this being the code suggested in the documentation it seems to give me an exception #pylint: disable=line-too-long
                    if not instance.user:
                        instance.user = request.user
                except ObjectDoesNotExist:
                    instance.user = request.user
                instance.save()
        else:
            formset.save()

class SampleInline(admin.TabularInline):
    """
        Used to display sample information associated to other types of data
    """
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id", "original_id", "project", "sample_type_link", "species_link",
        "tissue_link", "condition_link", "storage_requirement_link"]
    exclude = ["description"]
    can_delete = False
    max_num = 0
    show_change_link = True


class SampleConditionInline(admin.TabularInline):
    """
        Used to display sample information associated to other types of data in the Condition
    """
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link",
        "species_link", "tissue_link", "condition_link", "storage_requirement_link"]
    exclude = [
        "description", "type", "tissue", "storage_requirement",
        "species", "sample_type", "project", "parent_process", "xrh_id_prefix"]
    can_delete = False
    max_num = 0

@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]
    ordering = ["name"]
    fields = ["name", "description"]
    inlines = [
        SampleConditionInline
    ]

class SampleSpeciesInline(admin.TabularInline):
    """
        Used to display sample information associated to other types of data in the species view
    """
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link",
        "species_link", "tissue_link", "condition_link", "storage_requirement_link"]
    exclude = [
        "description", "type", "tissue", "storage_requirement",
        "condition", "sample_type", "project", "parent_process", "xrh_id_prefix"]
    can_delete = False
    max_num = 0

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [
        SampleSpeciesInline
    ]

class SampleStorageRequirementInline(admin.TabularInline):
    """
        Used to display sample information associated to other
        types of data in the storage requirement view
    """
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link",
        "species_link", "tissue_link", "condition", "storage_requirement_link"]
    exclude = [
        "description", "type", "tissue", "species",
        "diesease_status", "sample_type", "project",
        "xrh_id_prefix", "parent_process"]
    can_delete = False
    max_num = 0

@admin.register(StorageRequirement)
class StorageRequirementAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [
        SampleStorageRequirementInline
    ]


class SampleTypeInline(admin.TabularInline):
    """
        Used to display sample information associated to other types of data in the type view
    """
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link",
        "species_link", "tissue_link", "condition_link", "storage_requirement_link"]
    fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link",
        "species_link", "tissue_link", "condition_link", "storage_requirement_link"]
    can_delete = False
    max_num = 0

class SampleTypeAttachmentInline(admin.TabularInline):
    model = SampleTypeAttachment
    extra = 0
    max_num = 0
    fields = ["name_link", "uploaded"]
    readonly_fields = ["name_link", "uploaded"]

    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class AddSampleTypeAttachmentInline(admin.StackedInline):
    verbose_name = "Attachment"
    model = SampleTypeAttachment
    extra = 1
    max_num = 1
    fields = ["name", "attachment", "notes"]

    def has_add_permission(self, request, obj=None):
        return True
    def has_view_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(SampleType)
class TypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    form=SampleTypeForm
    ordering = ["name", "suffix"]
    fields = ["name", "suffix", "additional_risks", "description"]
    inlines = [
        SampleTypeAttachmentInline,
        AddSampleTypeAttachmentInline,
        SampleTypeInline
    ]
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["suffix"]
        return []


class SampleTissueInline(admin.TabularInline):
    """
        Used to display sample information associated to other types of data in the tissue view
    """
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link", "species_link",
        "tissue_link", "condition_link", "storage_requirement_link"]
    exclude = [
        "description", "type", "sample_type", "species",
        "condition", "storage_requirement", "project", "parent_process", "xrh_id_prefix"]
    can_delete = False
    max_num = 0

@admin.register(Tissue)
class TissueAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [
        SampleTissueInline
    ]


@admin.register(SampleIdPrefix)
class SampleIdPrefixAdmin(admin.ModelAdmin):
    """
        Aministration for the sample ID prefixes eg: SXAA
    """
    form = SampleIdPrefixForm
    search_fields = ["prefix"]
    ordering = ["prefix"]
    list_display = ["prefix", "description"]


@admin.register(Stain)
class StainAdmin(admin.ModelAdmin):
    """
        Admin panel for the stain opions
    """
    list_display = ["name", "description"]
    ordering = ["name"]
    def get_readonly_fields(self, request, obj=None):
        """
            Fields that should be editable at create but not after
        """
        if obj:
            return ["name"]
        return []

@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    list_display = ["name", "description"]
    ordering = ["name"]
    def get_readonly_fields(self, request, obj=None):
        """
            Fields that should be editable at create but not after
        """
        if obj:
            return ["name"]
        return []

class SampleProcessInline(admin.TabularInline):
    model = Sample
    extra = 0
    readonly_fields = [
        "xrh_id_link"
        ]
    fields = ["xrh_id_link"]
    exclude = [
        "description", "type", "tissue", "storage_requirement",
        "condition", "sample_type", "project",
        "original_id", "xrh_id_prefix", "species"]
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False



@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    form = ProcessForm
    list_display = ["__str__", "date", "user"]
    ordering = ["-date", "sample"]
    autocomplete_fields = ["sample", "process", "user"]
    fieldsets = [
        ("Process Details", {"fields": ["sample", "process", "user", "date"]}),
        ("Sectioning Details", {"fields": ["start_slice", "number_of_slices", "block_left"]}),
        ("Note", {"fields": ["notes"]})
    ]
    inlines = [
        SampleProcessInline
    ]
    def get_readonly_fields(self, request, obj=None):
        """
            Fields that should be editable at create but not after
        """
        if obj:
            return [
                "sample", "process", "user", "date",
                "start_slice", "number_of_slices", "block_left",
                "stain_used"]
        return []


@admin.register(SampleAttachment)
class SampleAttachmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ["sample", "attachment_type"]
    readonly_fields = ["uploaded", "preview"]
    fields = ["sample", "name", "attachment_type", "attachment", "uploaded", "notes", "preview"]
    list_display = ["sample", "attachment_type", "name"]
    ordering = ["sample", "attachment_type", "name"]
    list_filter = ["attachment_type"]

@admin.register(SampleAttachmentType)
class SampleAttachmentTypeAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    ordering = ["name"]
    search_fields = ["name"]


class ReportScanInline(admin.TabularInline):
    model = ReportScanMapping
    formset = RequiredInlineFormSet
    verbose_name = "Scan"
    verbose_name_plural = "Scans"
    extra = 1
    can_delete = False
    readonly_fields = ["scan_id_link", "filename", "scan_id", "scan_date", "scan_type"]
    autocomplete_fields = ["scan"]
    fields = ["scan", "scan_id_link", "scan_date", "scan_type"]

    def scan_type(self, instance):
        return instance.scan.scan_type()

    def scan_date(self, instance):
        return instance.scan.scan_date

    def scan_id(self, instance):
        return instance.scan.pk

    def filename(self, instance):
        return instance.scan.filename

    def has_add_permission(self, request, obj=None):
        return not obj
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request,obj=None):
        return not obj

@admin.register(SampleReport)
class SampleReportAdmin(admin.ModelAdmin):
    form = SampleReportForm
    search_fields = [
        "sample__full_xrh_id", "project__name", "project__full_title",
        "date_generated", "sample__original_id"]
    fields =[
        "sample", "project", "report", "date_generated", "generation_success",
        ("returned_photos", "generic_photos",),
        ("projections", "xy_slice"),
        ("yz_slice_roll_position", "xz_slice_roll_position", "xy_slice_roll_position"),
        ("thick_slice_mip_position", "thick_slice_avg_position",
            "thick_slice_stdev_position", "thick_slice_sum_position"),
        ("mip_3d_position", "volume_3d_position"),
        ("xray_360_position", "additional_videos_position"),
        "generation_errors", "generation_warnings", "further_analysis_text",]
    list_display = [
        "sample", "original_id", "project", "count_video_types", "generated_by",
        "date_generated", "generation_success"
    ]
    ordering = ["-date_generated", "sample"]
    list_filter = ["generation_success", "generated_by"]
    inlines = [
        ReportScanInline
    ]
    readonly_fields = [
        "date_generated", "generation_success", "generation_warnings", "report",
        "generation_errors", "original_id", "project_link", "sample_link",
        "generated_by", "count_video_types"
        ]
    actions = [
        "create_zip_bundle"
    ]

    def create_zip_bundle(self, request, queryset):
        bundle = create_report_bundle(queryset)
        wrapper = DeletingFileWrapper(open(bundle.name, "rb"))
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=reports.zip'
        response['Content-Length'] = bundle.tell()
        bundle.seek(0)
        return response
    create_zip_bundle.short_description = "Create Zip bundle"


    def get_fields(self, request, obj=None):
        if obj:
            return [
            "sample_link", "project_link", "report", "date_generated",
            ("generation_success", "generated_by"),
            "count_video_types",
            ("returned_photos", "generic_photos",),
            ("projections", "xy_slice"),
            ("yz_slice_roll_position", "xz_slice_roll_position", "xy_slice_roll_position"),
            ("thick_slice_mip_position", "thick_slice_avg_position",
                "thick_slice_stdev_position", "thick_slice_sum_position"),
            ("mip_3d_position", "volume_3d_position"),
            ("xray_360_position", "additional_videos_position"),
            "generation_errors", "generation_warnings", "further_analysis_text",]
        return [
        "sample", "project", "report", "date_generated", "generation_success",
        ("returned_photos", "generic_photos",),
        ("projections", "xy_slice"),
        ("yz_slice_roll_position", "xz_slice_roll_position", "xy_slice_roll_position"),
        ("thick_slice_mip_position", "thick_slice_avg_position",
            "thick_slice_stdev_position", "thick_slice_sum_position"),
        ("mip_3d_position", "volume_3d_position"),
        ("xray_360_position", "additional_videos_position"),
        "generation_errors", "generation_warnings", "further_analysis_text",]

    def count_video_types(self, instance):
        return instance.count_video_types()
    count_video_types.short_description = "No. of video types"

    def project_link(self, instance):
        return instance.project.str_link()
    project_link.short_description = "Project"

    def sample_link(self, instance):
        return instance.sample.xrh_id_link()
    sample_link.short_description = "Sample"

    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request,obj=None):
        return False

    def original_id(self, instance):
        return instance.sample.original_id

    def save_model(self, request, obj, form, change):
        obj.generated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SampleTypeAttachment)
class SampleTypeAttachmentadmin(admin.ModelAdmin):
    readonly_fields = ["uploaded"]
    fields = ["name", "sample_type", "uploaded", "attachment", "notes"]
    list_display = ["name", "sample_type", "uploaded"]
    ordering = ["name", "sample_type", "-uploaded"]
    list_filter = ["sample_type"]
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class SampleExtractionInline(admin.TabularInline):
    model = Sample
    extra = 0
    fields =  [
        "xrh_id_link", "original_id", "project_links", "sample_type_link", "species_link",
        "tissue_link", "condition_link", "storage_requirement_link"]
    readonly_fields = [
        "xrh_id_link", "original_id", "project_links", "sample_type_link", "species_link",
        "tissue_link", "condition_link", "storage_requirement_link"]
    can_delete = False
    max_num = 0


@admin.register(ExtractionMethod)
class ExtractionMethodAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [
        SampleExtractionInline
    ]
