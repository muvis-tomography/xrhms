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
from django.contrib import admin

# Register your models here.
from projects.models import ProjectMuvisMapping
from samples.models import SampleMuvisMapping
from scans.models import Scan

from .models import MuvisBug, BugzillaStatus, BugzillaResolution

class SampleLinkInline(admin.TabularInline):
    list_select_related = True
    model = SampleMuvisMapping
    verbose_name  = "Related sample"
    verbose_name_plural = "Related samples"
    max_rows = 0
    extra = 0
    fields = ["sample_link"]
    readonly_fields = ["sample_link"]
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class SampleAddInline(admin.StackedInline):
    model = SampleMuvisMapping
    verbose_name  = "Related sample"
    verbose_name_plural = "Related samples"
    autocomplete_fields = ["sample"]
    max_rows = 1
    extra = 1
    fields = ["sample"]
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return True
    def has_view_permission(self, request, obj=None):
        return False

class ScanInline(admin.TabularInline):
    model = Scan
    readonly_fields = ["name_link", "scan_type", "dataset_status", "sample_link"]
    fields = ["name_link", "scan_date", "operator", "scan_type", "dataset_status", "sample_link"]
    ordering = ["scan_date"]
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProjectLinkInline(admin.TabularInline):
    list_select_related = True
    model = ProjectMuvisMapping
    verbose_name  = "Related project"
    verbose_name_plural = "Related projects"
    max_rows = 0
    extra = 0
    fields = ["project_link"]
    readonly_fields = ["project_link"]
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class ProjectAddInline(admin.StackedInline):
    model = ProjectMuvisMapping
    verbose_name  = "Related project"
    verbose_name_plural = "Related projects"
    autocomplete_fields = ["project"]
    max_rows = 1
    extra = 1
    fields = ["project"]
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return True
    def has_view_permission(self, request, obj=None):
        return False


@admin.register(MuvisBug)
class BugAdmin(admin.ModelAdmin):
    list_display = ["muvis_id", "title", "status", "resolution"]
    list_filter = ["status", "resolution"]
    search_fields = ["muvis_id", "title"]
    fields = [
        "muvis_id", "title", "status", "resolution",
        "verbose_link", "no_scans", "estimate_total_scan_time",
    ]
    ordering = ["-muvis_id"]
    inlines = [
        SampleLinkInline,
        ProjectLinkInline,
        SampleAddInline,
        ProjectAddInline,
        ScanInline
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BugzillaStatus)
class BugStatusAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(BugzillaResolution)
class BugzillaResolutionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
