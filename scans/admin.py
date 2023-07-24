#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use, too-many-lines
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
from django.utils.html import mark_safe
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter
)

from xrh_utils import validate_user
from samples.models import ReportScanMapping
from labels.utils import print_drive_label
from .models import (
    ArchiveDrive,
    Gain,
    Machine,
    NikonCTScan,
    OmeData,
    OmeDetector,
    OmeImage,
    OmeObjective,
    OmePlane,
    RefinedRawData,
    RefinedRawExtension,
    Scan,
    ScanAttachment,
    ScanAttachmentType,
    ScanAttachmentTypeSuffix,
    ScannerScreenshot,
    ScheduledMove,
    Server,
    Share,
    Staining,
    StainingAttachment,
    TARGET_METAL_CHOICES,
    UserCopy
)

from .views import scan_comparison_csv, transfer_time_table


from .models.dataset_status import DATASET_MISSING, DATASET_DELETED
# Register your models here.

from .reports import generate_basic_report_tasks


PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 400

@admin.register(Gain)
class GainAdmin(admin.ModelAdmin):
    list_display = ["scanner", "gain_type", "index", "value"]
    list_filter = ["scanner", "gain_type"]
    ordering = ["scanner", "gain_type", "index"]

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = [
        "host_name", "internal_name", "internal_ipv4_address",
        "internal_ipv6_address", "external_name", "external_ipv4_address",
        "external_ipv6_address"]
    fieldsets = [
        ("Overview", {"fields": ["host_name"]}),
        ("Internal", {"fields": [
            "internal_name", "internal_ipv4_address", "internal_ipv6_address"]}),
        ("External", {"fields": [
            "external_name", "external_ipv4_address", "external_ipv6_address"]})
    ]


class ShareNikonScanInline(admin.TabularInline):
    model = NikonCTScan
    readonly_fields = ["filename_link"]
    fields = ["filename_link", "scan_date", "operator", "sample"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ["name", "server"]
    readonly_fields = [
        "internal_mnt_path", "internal_ipv4_mnt_path", "internal_ipv6_mnt_path",
        "external_mnt_path", "external_ipv4_mnt_path", "external_ipv6_mnt_path"
    ]
    fieldsets = [
        ("Overview", {"fields": [
            "name", "server", "generate_extra_folder", "default_status",
            ("linux_mnt_point", "windows_mnt_point")]}),
        ("Internal", {"fields": [
            "internal_mnt_path", "internal_ipv4_mnt_path", "internal_ipv6_mnt_path"]}),
        ("External", {"fields": [
            "external_mnt_path", "external_ipv4_mnt_path", "external_ipv6_mnt_path"]})

    ]
    inlines = [
        ShareNikonScanInline
    ]

class MachineNikonCTScanInline(admin.TabularInline):
    model = NikonCTScan
    readonly_fields = ["filename_link"]
    fields = ["filename_link", "scan_date", "operator", "sample"]
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MachineGainInline(admin.TabularInline):
    model = Gain
    fields = ["gain_type", "index", "value"]
    ordering = ["gain_type", "index"]
    extra = 0
    def has_change_permission(self, request, obj=None):
        return False

class MachineScreenshotInline(admin.StackedInline):
    model = ScannerScreenshot
    fields = ["screen_number", "image_timestamp", "preview"]
    ordering = ["screen_number"]
    extra = 0
    readonly_fields = ["preview", "image_timestamp"]
    fields = ["image_timestamp", "preview"]

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    inlines = [
        MachineScreenshotInline,
        MachineGainInline,
        MachineNikonCTScanInline,
    ]

class ScanAttachmentInline(admin.TabularInline):
    verbose_name = "Attachment"
    verbose_name_plural = "Attachments"
    model = ScanAttachment
    max_rows = 1
    extra = 0
    readonly_fields = ["name_link", "attachment_type", "notes", "uploaded"]
    fields = [
        "name_link", "attachment_type", "uploaded", "to_upload", "url",
        "exclude_from_report", "editable"
    ]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class ScanAttachmentAddInline(admin.StackedInline):
    model = ScanAttachment
    verbose_name = "Add Attachment"
    verbose_name = "Add Attachments"
    max_rows = 1
    extra = 1
    fields = [
        "name", "attachment", "attachment_type", "url", "to_upload", "overlay_position",
        "exclude_from_report", "notes"
    ]

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_view_permission(self, request, obj=None):
        return False


class ScanReportInline(admin.TabularInline):
    model = ReportScanMapping
    verbose_name_plural = "Reports"
    max_rows = 0
    extra = 0
    fields = ("link", "generation_success")
    readonly_fields = ("link", "generation_success")

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class RefinedRawDataInline(admin.TabularInline):
    model = RefinedRawData
    max_rows = 0
    extra = 0
    fields = [
        "name_link", "path",
        ("first_indexed", "last_updated", "file_modified"),
        "shareable", "file_available", "notes"
    ]

    readonly_fields = [
        "name_link", "path", "file_available",
        "first_indexed", "last_updated", "file_modified"
    ]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


class ChildScanInline(admin.TabularInline):
    verbose_name="Child scan"
    verbose_name_plural="Child scans"
    model=Scan
    max_rows=0
    extra=0
    fields = [
        "scan_link", "scan_date"
    ]
    readonly_fields = [
        "scan_link"
    ]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(NikonCTScan)
class NikonCTScanAdmin(PolymorphicChildModelAdmin):
    base_model = NikonCTScan
    verbose_name = "Nikon CT Scan"
    verbose_name_plural = "Nikon CT Scans"
    fieldsets = [
        ("Overview", {"fields": [
            "name", "id", "scan_date", "inserted", "scanner_link", "operator",
            "sample", "sample_link", "parent_link",
            "share_link", "path",
            "filename", "muvis_bug_link", "operator_id", "modifier_id", "checksum",
            "file_available","notes", "extra_listing", "extra_listing_last_updated"]}),
        ("Projections", {"fields": [
            ("projection0deg_img", "projection90deg_img", "xyslice_img")]}),
        ("Paths", {"fields": [
            "internal_mnt_path", "internal_ipv4_mnt_path", "internal_ipv6_mnt_path",
            "external_mnt_path", "external_ipv4_mnt_path", "external_ipv6_mnt_path",
        ],'classes': ('collapse',)}),
        ("Folders", {"fields": [
            "input_separator", "input_folder_name", "input_name", "input_digits",
             "output_separator", "output_folder_name", "output_name", "output_digits"]}),
        ("X-Ray conditions", {"fields":[
            "xray_kv", "xray_ua", "power",  "xray_head", "target_metal",
            "filter_type", "filter_thickness_mm",
            "filter_material", "filter_preset"
        ]}),
        ("Imaging Settings - Geometry", {"fields":[
            "src_to_object", "src_to_detector", "src_to_virtual_detector",
            "geometric_magnification",
        ]}),
        ("Imaging Settings - Aquisition", {"fields":[
            "projections", "initial_angle", "angular_step", "pitch", "shuttling_text",
            "max_pixels_to_shuttle", "scan_mode",
            "frames_per_projection", "exposure", "accumulation", "accumulation_readable",
            "binning", "binning_readable",
            "gain", "analog_gain_readable", "digital_gain", "digital_gain_readable",
            "brightness", "white_to_black_latency", "black_to_white_latency",
            "white_to_white_latency", "estimate_time"
        ]}),
        ("Imaging Settings - Dimensions", {"fields":[
            "units",
            "voxels_x", "voxel_size_x", "offset_x",
            "voxels_y", "voxel_size_y", "offset_y",
            "voxels_z", "voxel_size_z", "offset_z",
            "mask_radius",
            "detector_pixels_x", "detector_pixel_size_x", "detector_offset_x",
            "detector_pixels_y", "detector_pixel_size_y", "detector_offset_y",
            "virtual_detector_pixels_x", "virtual_detector_pixel_size_x",
            "virtual_detector_offset_x",
            "virtual_detector_pixels_y", "virtual_detector_pixel_size_y",
            "virtual_detector_offset_y",
            "region_start_x", "region_pixels_x",
            "region_start_y", "region_pixels_y",
            "scaling","output_units", "scale", "voxel_scaling_factor",
            "object_offset_x", "object_offset_y",
            "object_offset_x_start", "object_offset_x_end",
            "object_tilt", "object_roll",
        ]}),
        ("Processing", {"fields": [
            "output_type", "import_conversion", "auto_scaling_type", "scaling_minimum",
            "scaling_maximum", "low_percentile", "high_percentile", "white_level",
            "interpolation_type", "beam_hardening_lut_file", "coef_x4", "coef_x3", "coef_x2",
            "coef_x1", "coef_x0", "cutoff_frequency", "exponent", "normalisation", "scattering",
            "median_filter_kernel_size", "convolution_kernel_size", "beam_hardening_preset",
            "automatic_geometry", "automatic_geometry_increment", "automatic_geometry_binning",
            "automatic_geometry_window", "version", "product", "veiling_glare_applied",
        ]}),
        ("Centre of Rotation", {"fields": [
            "centre_of_rotation_top", "centre_of_rotation_bottom", "automatic_centre_of_rotation",
            "automatic_centre_of_rotation_offset_z1", "automatic_centre_of_rotation_offset_z2",
            "automatic_centre_of_rotation_mask_radius"
        ]}),
        ("Helical", {"fields": [
            "helical_continuous_scan", "helical_derivative_type", "helical_sample_top",
            "helical_sample_bottom", "helical_projections_per_rotation",
            "helical_rotations",
            "helical_upper_position_checked", "helical_lower_position_checked",
            "helical_upper_check_position", "helical_lower_check_position",
            "helical_upper_magnification_position", "helical_lower_magnification_position"
        ]}),
        ("Misc", {"fields": [
            "dicom", "lines", "increment", "derivative_type", "blanking", "order_fft",
            "autocor_num_bands", "cor_auto_accuracy", "slice_height_mm_single",
            "slice_height_mm_dual_top", "slice_height_mm_dual_bottom", "angle_file_use",
            "angle_file_ignore_errors", "timestamp_folder"
        ]})
    ]
    inlines = [
        ScanAttachmentInline,
        ScanAttachmentAddInline,
        RefinedRawDataInline,
        ChildScanInline,
        ScanReportInline,
    ]
    autocomplete_fields = ["sample"]

    def has_add_permission(self, request): #pylint:disable=unused-argument
        return False



    def get_readonly_fields(self, request, obj=None):
        always = [
            "name", "scan_date", "inserted", "scanner_link", "operator", "share_link", "path",
            "muvis_bug_link", "operator_id", "filename", "checksum", "id", "sample_link",
            "internal_mnt_path", "internal_ipv4_mnt_path", "internal_ipv6_mnt_path",
            "external_mnt_path", "external_ipv4_mnt_path", "external_ipv6_mnt_path",
            "input_separator", "input_folder_name", "output_separator", "output_folder_name",
            "voxels_x", "voxel_size_x", "offset_x",
            "voxels_y", "voxel_size_y", "offset_y",
            "voxels_z", "voxel_size_z", "offset_z",
            "src_to_object", "src_to_detector", "mask_radius",
            "detector_pixels_x", "detector_pixel_size_x", "detector_offset_x",
            "detector_pixels_y", "detector_pixel_size_y", "detector_offset_y",
            "region_start_x", "region_pixels_x",
            "region_start_y", "region_pixels_y",
            "projections", "initial_angle", "angular_step",
            "units", "scaling", "output_units", "scale", "voxel_scaling_factor", "object_offset_x",
            "object_roll", "pitch", "object_offset_x_start", "object_offset_x_end",
            "xray_kv", "xray_ua", "shuttling_text", "exposure", "accumulation", "binning", "gain",
            "frames_per_projection", "digital_gain", "brightness", "white_to_black_latency",
            "black_to_white_latency", "white_to_white_latency",
            "output_type", "import_conversion", "auto_scaling_type", "scaling_minimum",
            "scaling_maximum", "low_percentile", "high_percentile", "white_level",
            "interpolation_type", "beam_hardening_lut_file", "coef_x4", "coef_x3", "coef_x2",
            "coef_x1", "coef_x0", "cutoff_frequency", "exponent", "normalisation", "scattering",
            "median_filter_kernel_size", "convolution_kernel_size", "beam_hardening_preset",
            "automatic_geometry", "automatic_geometry_increment", "automatic_geometry_binning",
            "automatic_geometry_window",
            "centre_of_rotation_top", "centre_of_rotation_bottom", "automatic_centre_of_rotation",
            "automatic_centre_of_rotation_offset_z1", "automatic_centre_of_rotation_offset_z2",
            "automatic_centre_of_rotation_mask_radius",
            "filter_type", "filter_thickness_mm", "filter_material", "filter_preset",
            "dicom", "lines", "increment", "derivative_type", "modifier_id", "input_name",
            "input_digits", "output_name", "output_digits", "virtual_detector_pixels_x",
            "virtual_detector_pixels_y", "virtual_detector_pixel_size_x",
            "virtual_detector_pixel_size_y", "virtual_detector_offset_x",
            "virtual_detector_offset_y",
            "src_to_virtual_detector", "object_offset_y", "object_tilt", "blanking", "order_fft",
            "version", "product", "autocor_num_bands", "cor_auto_accuracy",
            "slice_height_mm_single",
            "slice_height_mm_dual_top", "slice_height_mm_dual_bottom", "angle_file_use",
            "angle_file_ignore_errors", "power", "timestamp_folder", "estimate_time",
            "binning_readable",
            "analog_gain_readable", "digital_gain_readable", "xray_head", "accumulation_readable",
            "projection0deg_img", "projection90deg_img", "xyslice_img", "geometric_magnification",
            "file_available", "extra_listing", "extra_listing_last_updated", "parent_link",
            "helical_continuous_scan", "helical_derivative_type", "helical_sample_top",
            "helical_sample_bottom", "helical_projections_per_rotation",
            "helical_upper_position_checked", "helical_lower_position_checked",
            "helical_upper_check_position", "helical_lower_check_position",
            "helical_upper_magnification_position", "helical_lower_magnification_position",
            "helical_rotations", "veiling_glare_applied", "max_pixels_to_shuttle", "scan_mode"
        ]
        if not obj:
            return always
        if request.user.is_superuser: # it's a super user
            return always
        readonly = always
        if obj.sample_id: #sample set
            readonly += ["sample"]
        if obj.target_metal:
            readonly += ["target_metal"]
        return readonly


    def estimate_time(self, instance):
        est = instance.estimate_time()
        if est:
            return est
        return "-"

    def xyslice_img(self, instance):
        return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint:disable=line-too-long
                instance.xyslice.url,
                instance.xyslice_png.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
    xyslice_img.short_description = "XY Slice"

    def projection0deg_img(self, instance):
        return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint:disable=line-too-long
                instance.projection0deg.url,
                instance.projection0deg_png.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
    projection0deg_img.short_description = "0 degrees projection"

    def projection90deg_img(self, instance):
        return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint:disable=line-too-long
                instance.projection90deg.url,
                instance.projection90deg_png.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
    projection90deg_img.short_description = "90 degrees projection"

    def response_change(self, request, obj):
        if "_basic_report" in request.POST:
            try:
                generate_basic_report_tasks(obj)
                messages.success(request, "Basic reports added to processing queue")
            except ValueError:
                messages.error(
                    request,
                    "Unable to add basic reports to processing queue, are both sample and projects set?") # pylint: disable=line-too-long
            return HttpResponseRedirect(reverse("admin:scans_scan_change", args=[obj.pk]))
        return super().response_change(request, obj)



@admin.register(ScanAttachment)
class ScanAttachmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ["scan", "attachment_type"]
    readonly_fields = ["uploaded", "preview"]
    fields = [
        "scan", "name", "attachment_type", "attachment", "uploaded", "url", "to_upload",
        "overlay_position", "exclude_from_report", "notes", "preview"
    ]
    list_display = ["name", "attachment_type", "scan", "to_upload", "publically_uploaded"]
    ordering = ["scan", "attachment_type", "name"]
    list_filter = ["attachment_type", "to_upload"]

    def get_readonly_fields(self, request, obj=None):
        always = ["uploaded", "preview"]
        if obj:
            if obj.url:
                always += ["url", "to_upload", "overlay_position"]
            return always + ["attachment", "scan", "attachment_type"]

        return always

    def has_change_permission(self, request, obj=None):
        if obj:
            return obj.editable
        return True

class ScanAttachmentTypeSuffixInline(admin.TabularInline):
    model = ScanAttachmentTypeSuffix
    verbose_name = "Search suffix"
    verbose_name_plural = "Search suffixes"
    max_rows = 0
    extra = 0
    fields = [
        "suffix",
    ]

@admin.register(ScanAttachmentType)
class ScanAttachmentTypeAdmin(admin.ModelAdmin):
    fields = ["name", "report_priority", "description", "include_in_extra_folder"]
    ordering = ["name"]
    search_fields = ["name"]

    inlines = [
        ScanAttachmentTypeSuffixInline
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name"]
        return []

@admin.register(Scan)
class ScanAdmin(PolymorphicParentModelAdmin):
    base_model = Scan
    child_models = [ NikonCTScan, OmeData]
    list_filter = ["scanner", PolymorphicChildModelFilter, "share", "dataset_status"]
    search_fields = ["filename", "sample__xrh_id_number", "pk", "sample__project__name"]
    polymorphic_list = True
    list_display = [
        "__str__", "scan_date", "sample_link", "scanner", "scan_type",
        "dataset_status", "dataset_status_last_updated", "estimate_time"]
    readonly_fields = ["estimate_time"]
    ordering = ["-scan_date"]
    autocomplete_fields = ["sample"]
    actions = [
        "move_dataset",
        "mark_deleted",
        "add_notes",
        "copy_to_user",
        "compare",
        "calculate_transfer",
        "set_target_material",
    ]

    def calculate_transfer(self, request, queryset):
        context = {}
        context["opts"] = Scan._meta
        context["is_popup"] = False
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        return transfer_time_table(request, queryset, context)
    calculate_transfer.short_description = "Calculate transfer times"

    def compare(self, request, queryset):
        return scan_comparison_csv(queryset)
    compare.short_description = "Compare scans"

    def copy_to_user(self, request, queryset):
        if 'apply' in request.POST:
            username = request.POST.get("username")
            if not validate_user(username):
                messages.error(request, "No user found for username {}".format(username))
                return HttpResponseRedirect(request.get_full_path())
            for scan in queryset:
                copy_obj = UserCopy()
                copy_obj.scan = scan
                copy_obj.username = username
                copy_obj.include_recon_data = bool(request.POST.get("reconstructed_data"))
                copy_obj.include_raw_data = bool(request.POST.get("raw_data"))
                copy_obj.save()
            messages.success(request, "Copy added for {} datasets".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())
        if 'abort' in request.POST:
            messages.info(request, "Add notes aborted")
            return HttpResponseRedirect(request.get_full_path())

        context = {}
        context["opts"] = Scan._meta
        context["is_popup"] = False
        context["scans"] = queryset
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        context["scans"] = queryset
        return render(request,
            "admin/scans/copy_to_user.html",
            context=context)

    copy_to_user.short_description = "Copy to a user's Readonly space"


    def set_target_material(self, request, queryset):
        if "apply" in request.POST:
            metal = request.POST.get("target")
            count = 0
            total = queryset.count()
            for scan in queryset:
                if not isinstance(scan, NikonCTScan):
                    continue
                if not scan.target_metal:
                    scan.target_metal = metal
                    scan.save()
                    count += 1
            messages.success(request, "Set target for {}/{} scans.".format(count, total))
            return HttpResponseRedirect(request.get_full_path())
        if "abort" in request.POST:
            messages.info(request, "Set target material aborted")
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["opts"] = Scan._meta
        context["is_popup"] = False
        context["scans"] = queryset
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        context["scans"] = queryset
        context["targets"] = TARGET_METAL_CHOICES
        return render(request,
            "admin/scans/bulk_set_target.html",
            context=context)


    set_target_material.short_description = "Set the target material"

    def add_notes(self, request, queryset):
        if 'apply' in request.POST:
            notes = "-----\n" + request.POST.get("notes") + "\n-----\n"
            for scan in queryset:
                if scan.notes:
                    scan.notes += notes
                else:
                    scan.notes = notes
                scan.save()
            messages.success(request, "Added notes to {} records".format(len(queryset)))
            return HttpResponseRedirect(request.get_full_path())
        if 'abort' in request.POST:
            messages.info(request, "Add notes aborted")
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["opts"] = Scan._meta
        context["is_popup"] = False
        context["scans"] = queryset
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        return render(request,
            "admin/scans/add_notes.html",
            context=context)
    add_notes.short_description = "Bulk add notes"

    def move_dataset(self, request, queryset):
        if 'apply' in request.POST:
            share_obj = Share.objects.get(pk=request.POST.get("share", ))
            group_by_sample = bool(request.POST.get("group_by_sample", ))
            for scan in queryset:
                sm = ScheduledMove() #pylint: disable=invalid-name
                sm.destination = share_obj
                sm.scan = scan
                sm.group_by_sample = group_by_sample
                sm.save()
            messages.success(request, "Scheduled moving of >={} scans".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        if 'abort' in request.POST:
            messages.info(request, "Move aborted")
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["opts"] = Scan._meta
        context["is_popup"] = False
        context["scans"] = queryset
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        share_set = Share.objects.all()
        shares = []
        for share_obj in share_set:
            share = {}
            share["pk"] = share_obj.pk
            share["name"] = str(share_obj)
            shares.append(share)
        context["shares"] = shares
        return render(request,
            "admin/scans/move_dataset.html",
            context=context)

    move_dataset.short_description = "Move selected datasets"

    def mark_deleted(self, request, queryset):
        marking_success =  0
        for scan in queryset:
            if scan.dataset_status == DATASET_MISSING:
                scan.dataset_status = DATASET_DELETED
                scan.save()
                marking_success += 1
        if marking_success == queryset.count():
            messages.success(request, "All ({}) datasets marked as deleted".format(marking_success))
        else:
            messages.error(
                request,
                "Some datasets ({}) failed to update. Their status must be missing".format(
                    queryset.count() - marking_success))
        return HttpResponseRedirect(request.get_full_path())

    mark_deleted.short_description = "Mark the selected datasets as deleted"


    def estimate_time(self, instance):
        #Check to see if the object has an estimate time function, if it does call it
        if getattr(instance, "estimate_time", None):
            return instance.estimate_time()
        return "-"
    estimate_time.short_description = "Estimated Time"

class OmeImageInline(admin.TabularInline):
    model = OmeImage
    max_rows = 0
    extra = 0
    verbose_name = "OME Image"
    verbose_name_plural = "OME Images"
    fields = ["id_link", "name_link", "objective_nominal_magnification", "scan_time_readable"]
    readonly_fields = [
        "objective_nominal_magnification", "id_link",
        "name_link", "scan_time_readable"
    ]

    def name_link(self, instance):
        url = reverse("admin:scans_omeimage_change", args=[instance.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, instance.name))
    name_link.short_description = "Name"

    def id_link(self, instance):
        url = reverse("admin:scans_omeimage_change", args=[instance.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, instance.image_id))
    id_link.short_description = "Image ID"


    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False



@admin.register(OmeData)
class OmeDataAdmin(PolymorphicChildModelAdmin):
    base_model = OmeData
    readonly_fields = [
        "name", "scan_date", "inserted", "scanner_link", "operator", "share_link", "path",
        "muvis_bug_link", "filename", "checksum", "id", "file_available",
        "internal_mnt_path", "internal_ipv4_mnt_path", "internal_ipv6_mnt_path",
        "external_mnt_path", "external_ipv4_mnt_path", "external_ipv6_mnt_path",
        "overview_img", "scan_time_readable",
    ]

    fieldsets = [
        ("Overview", {"fields": [
            "name", "id", "scan_date", "inserted", "scanner_link", "scan_time_readable",
            "operator", "sample", "share_link", "path",
            "filename", "muvis_bug_link", "checksum", "file_available",
            "staining", "staining_notes",
            "overview_img", "notes"]}),
        ("Paths", {"fields": [
            "internal_mnt_path", "internal_ipv4_mnt_path", "internal_ipv6_mnt_path",
            "external_mnt_path", "external_ipv4_mnt_path", "external_ipv6_mnt_path",
        ],'classes': ('collapse',)}),
    ]
    inlines = [
        OmeImageInline,
        ScanAttachmentInline,
        ScanAttachmentAddInline,
    ]

    def overview_img(self, instance):
        return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint: disable=line-too-long
            instance.overview.url,
            instance.overview.url,
            PREVIEW_WIDTH, PREVIEW_HEIGHT))
    overview_img.short_description = "Overview"



@admin.register(ScannerScreenshot)
class ScannerScreenshotAdmin(admin.ModelAdmin):
    list_display = ["scanner", "screen_number", "image_timestamp"]
    list_filter = ["scanner"]
    ordering = ["scanner", "screen_number"]
    fields = ["scanner", "screen_number", "image_timestamp", "attachment", "preview"]
    readonly_fields = ["image_timestamp", "preview"]

@admin.register(ScheduledMove)
class ScheduledMoveAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "scan_link", "destination", "group_by_sample", "date_queued",
        "date_executed", "success"
    ]
    ordering = ["-date_queued", "scan"]
    fields = [
        "scan_link", "destination", "group_by_sample", "date_queued",
        "date_executed", "success", "output"
    ]
    list_filter = ["destination", "group_by_sample", "success"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        if not obj: # No object exists
            return True
        if not obj.date_executed: # it is in the queue and han't run yet
            return True
        return False # it's already run


@admin.register(ArchiveDrive)
class ArchiveDriveAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "date_created", "manufacturer", "serial_number", "capacity"
    ]
    list_filter = [
        "manufacturer", "capacity"
    ]
    readonly_fields = [
        "pk", "date_created", "qr_code_img", "estimated_usage", "no_files",
        "estimated_free",
    ]
    fields = [
        "pk", "date_created", "manufacturer", "serial_number",
        "qr_code_img", "no_files", ("capacity", "estimated_usage", "estimated_free")
    ]

    def qr_code_img(self, instance):
        return mark_safe('<img src="{}"/>'.format(instance.qr_code.url))
    qr_code_img.short_description = "QR code"

    def response_change(self, request, obj):
        if "_print_label" in request.POST:
            if print_drive_label(obj):
                messages.success(request, "Label sent for printing.")
            else:
                messages.error(request, "Failed to send label for printing.")
            return HttpResponseRedirect(reverse('admin:scans_archivedrive_change', args=[obj.id]))
        return super().response_change(request, obj)


#@admin.register(OmePlane)
class OmePlaneAdmin(admin.ModelAdmin):
    readonly_fields = [
        "exposure", "position_x", "position_y", "t", "z", "channel_name",
        "channel_id", "samples_per_pixel", "binning", "detector_gain", "detector"
    ]

    fields = [
        "channel_name", "channel_id", "exposure", "position_x", "position_y", "t", "z",
        "samples_per_pixel", "binning", "detector_gain", "detector"
    ]

    def channel_name(self, instance):
        name = instance.channel.name
        if name:
            return name
        return "-"

    def wavelength(self, instance):
        wavelength = instance.channel.wavelength
        if wavelength:
            return wavelength
        return "-"

    def channel_id(self, instance):
        return instance.channel.channel_id
    channel_id.short_description = "Channel ID"

    def samples_per_pixel(self, instance):
        samples = instance.channel.samples_per_pixel
        if samples:
            return samples
        return "-"

    def binning(self, instance):
        binning = instance.channel.binning
        if binning:
            return binning
        return "-"

    def detector_gain(self, instance):
        gain = instance.channel.detector_gain
        if gain:
            return gain
        return "-"
    def detector(self, instance):
        detector = instance.channel.detector
        if detector:
            url = reverse('admin:scans_omedetector_change', args=[detector.pk])
            return mark_safe('<a href="{}">{}</a>'.format(url, str(detector)))
        return "-"

@admin.register(OmeDetector)
class OmeDetectorAdmin(admin.ModelAdmin):
    list_display = [
        "manufacturer", "model", "serial_number", "detector_type", "gain",
    ]
    list_filter = [
        "manufacturer", "model", "detector_type"
    ]
    readonly_fields = [
        "manufacturer", "model", "serial_number", "detector_type", "gain",
    ]
    fields = [
        "manufacturer", "model", "serial_number", "detector_type", "gain",
    ]

@admin.register(OmeObjective)
class OmeObjectiveAdmin(admin.ModelAdmin):
    list_display = [
        "model", "lens_na", "nominal_magnification", "working_distance"
    ]
    fields = [
        "model", "lens_na", "nominal_magnification", "working_distance"
    ]
    readonly_fields = [
        "model", "lens_na", "nominal_magnification", "working_distance"
    ]

class StainingAttachmentInline(admin.TabularInline):
    max_rows = 0
    extra = 0
    model=StainingAttachment
    ordering=["name"]
    list_display = ["name", "attachment", "notes"]
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Staining)
class StainingAdmin(admin.ModelAdmin):
    list_display = ["protocol_name"]
    ordering = ["protocol_name"]
    fields = ["protocol_name", "protocol"]
    readonly_fields = ["protocol_name", "protocol"]
    inlines = [StainingAttachmentInline]

    def get_readonly_fields(self, request, obj=None):
        always = []
        if obj:
            return always + ["protocol_name", "protocol"]

        return always

class OmePlaneInline(admin.StackedInline):
    model = OmePlane
    max_rows = 0
    extra = 0
    verbose_name = "OME Plane"
    verbose_name_plural = "OME Planes"
    readonly_fields = [
        "channel_name", "filename", "exposure", "position_x", "position_y", "t", "z",
        "wavelength", "samples_per_pixel", "binning", "preview_img"
    ]

    fields = [
        ("channel_name", "filename"),
        ("exposure", "wavelength", "samples_per_pixel", "binning"),
        ("position_x", "position_y", "t", "z"),
        "preview_img",
    ]

    def preview_img(self, instance):
        if not instance.preview:
            return "-"
        return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint: disable=line-too-long
                instance.preview.url,
                instance.preview.url,
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT))
    preview_img.short_description = "Preview"

    def channel_name(self, instance):
        name = instance.channel.name
        if name:
            return name
        return "-"

    def wavelength(self, instance):
        wavelength = instance.channel.emission_wavelength
        if wavelength:
            return wavelength
        return "-"

    def samples_per_pixel(self, instance):
        return instance.channel.samples_per_pixel

    def binning(self, instance):
        return instance.channel.binning

    def exposure(self, instance):
        return instance.exposure

    def position_x(self, instance):
        return instance.omeplane.position_x

    def position_y(self, instance):
        return instance.omeplane.position_y

    def t(self, instance): #pylint:disable=invalid-name
        return instance.omeplane.t

    def z(self, instance): #pylint:disable=invalid-name
        return instance.omeplane.z
@admin.register(OmeImage)
class OmeImageAdmin(admin.ModelAdmin):
    list_display = ["scan", "name", "objective_nominal_magnification"]
    ordering = ["scan", "name"]
    fields = [
        "scan_link", "image_id", "name", "scan_time", "filename",
        ("objective_model", "objective_nominal_magnification"),
        ("pixels_big_endian", "pixels_dimension_order", "pixels_interleaved"),
        ("pixels_significant_bits", "pixels_type"),
        ("physical_size_x", "physical_size_y"),
        ("pixels_x", "pixels_y", "size_c", "size_z", "size_t"),
        "refractive_index", "preview_img",
    ]
    readonly_fields = ["objective_model", "objective_nominal_magnification", "preview_img"]
    inlines = [
        OmePlaneInline
    ]

    def scan_link(self, instance):
        url = reverse("admin:scans_scan_change", args=[instance.scan_id])
        return mark_safe('<a href={}>{}</a>'.format(url, instance.scan))
    scan_link.short_description = "Scan"

    def preview_img(self, instance):
        return mark_safe(
            '<a href="{}" target="_new"><img src="{}" style="max-width:{}px; max-height:{}px;"/></a>'.format( #pylint:disable=line-too-long
            instance.preview.url,
            instance.preview.url,
            PREVIEW_WIDTH, PREVIEW_HEIGHT))
    preview_img.short_description = "Preview"

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(RefinedRawExtension)
class RefinedRawExtensionAdmin(admin.ModelAdmin):
    list_display = ["extension"]
    ordering = ["extension"]
    fields = ["extension", "notes"]

@admin.register(RefinedRawData)
class RefinedRawDataAdmin(admin.ModelAdmin):
    list_display = ["scan", "name", "shareable", "file_available"]
    ordering = ["scan", "shareable", "file_available"]
    fields = [
        "scan_link", "name", "path",
        ("first_indexed", "file_modified", "last_updated"),
        "checksum", "shareable", "file_available", "notes"
    ]
    readonly_fields = [
        "scan_link", "name", "path",
        "first_indexed", "last_updated",
        "checksum", "file_available", "file_modified"

    ]

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserCopy)
class UserCopyAdmin(admin.ModelAdmin):
    list_display = ["username", "scan", "date_added", "copy_success", "deletion_success"]
    ordering = ["username", "scan", "date_added"]
    list_filter = ["copy_success", "deletion_success", "include_recon_data", "include_raw_data"]
    search_fields = ["username", "scan", "date_added"]
    fields = [
        "scan", "username",
        "date_added",
        ("include_raw_data", "include_recon_data"),
        ("date_copied", "copy_success"),
        ("deletion_after", "deletion_valid_from"),
        ("date_deleted", "deletion_success"),
        "cmd_output",
    ]
    readonly_fields = [
        "deletion_valid_from", "date_added"
    ]
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        if not obj: # No object exists
            return True
        if not obj.date_copied: # it is in the queue and han't run yet
            return True
        return False # it's already run

    def has_add_permission(self, request):
        return False
