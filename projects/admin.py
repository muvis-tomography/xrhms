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
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.html import mark_safe
from django.urls import reverse
from django.contrib import admin, messages
from django.shortcuts import render
from samples.models import SampleReport
from labels.utils import (
    print_project_label, LA62_PRINTER_11354, LB68_PRINTER_11354,
    print_address_label,
)
from .models import (
    Contact, Funder, Institution, Project, ProjectAttachment,
    ProjectStatus, ProjectUpdate, ProjectMuvisMapping
)

from .views import contact_details_csv
# Register your models here.


class ReportInline(admin.TabularInline):
    model = SampleReport
    max_rows = 0
    extra = 0
    classes = ["collapse"]
    ordering = ["-date_generated"]
    readonly_fields = ["date_generated_link", "original_id"]
    fields = ["sample", "original_id", "date_generated_link", "generation_success"]

    def original_id(self, instance):
        original_id = instance.sample.original_id
        if not original_id:
            original_id = "-"
        return original_id
    original_id.short_description = "Original ID"


    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class OtherContactInline(admin.TabularInline):
    extra = 0
    verbose_name = "contact"
    verbose_name_plural = "Other Contacts"
#    readonly_fields = ["name", "email", "phone", "address"]
    list_display = ("name", "email", "phone")
    model = Project.other_contacts.through


class SampleInline(admin.TabularInline):
    model = Project.sample_set.through
    list_select_related = True
    readonly_fields = [
        "xrh_id", "original_id", "sample_species", "sample_type", "tissue", "date_entered",
        "current_location_link",
    ]
    fields = [
        "xrh_id", "original_id", "sample_species", "sample_type", "tissue", "date_entered",
        "current_location_link",
    ]
    verbose_name =  "Sample"
    verbose_name_plural = "Samples"
    extra = 0
    max_num = 10
    def xrh_id(self, instance):
        url =  reverse('admin:samples_sample_change', args=[instance.sample.pk])
        return mark_safe('<a href="{}">{}</a>'.format(url, instance.sample.xrh_id()))
    xrh_id.short_description = "XRH ID"

    def original_id(self, instance):
        original_id = instance.sample.original_id
        if not original_id:
            original_id = "-"
        return original_id
    original_id.short_description = "Original ID"

    def sample_species(self, instance):
        return instance.sample.species_link()
    sample_species.short_description = "Species"

    def sample_type(self, instance):
        return instance.sample.sample_type_link()
    sample_type.short_description = "Sample Type"

    def tissue(self, instance):
        return instance.sample.tissue_link()
    tissue.short_description = "Tissue"

    def date_entered(self, instance):
        return instance.sample.date_entered.strftime("%Y-%m-%d")
    date_entered.short_description = "Date entered"

    def current_location_link(self, instance):
        return instance.sample.current_location_link()
    current_location_link.short_description = "Current Location / Status"

    def has_add_permission(self, request, obj=None):
        return False

class ProjectStatusInline(admin.TabularInline):
    list_select_related = True
    model = ProjectUpdate
    extra = 0
    max_rows = 0
    ordering = ["-last_updated"]
    fields = [
        "status", "user", "last_updated", "last_action", "last_action_date",
        "notes", "next_action", "next_action_deadline", "next_action_status"]
    readonly_fields = [
        "project", "status", "user", "last_updated", "last_action_date",
        "last_action", "notes", "next_action", "next_action_deadline"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class AddProjectStatusInline(admin.StackedInline):
    model=ProjectUpdate
    extra = 1
    max_rows = 1
    field = [
        "status", "last_updated", "last_action", "last_action_date",
        "notes", "next_action", "next_action_deadline"]
    exclude = ["user", "next_action_status"]
    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

class MuvisBugLinkInline(admin.TabularInline):
    verbose_name = "Related Muvis bug"
    verbose_name_plural = "Related Muvis bugs"
    model=ProjectMuvisMapping
    list_select_related = True
    max_rows = 0
    extra = 0
    fields = ["bugzilla_link", "muvis_link", "status", "resolution"]
    readonly_fields = ["muvis_link", "status", "resolution", "bugzilla_link"]

    def title(self, instance):
        return instance.muvis_id.title

    def status(self, instance):
        return instance.muvis_id.status
    status.short_description = "Status"

    def resolution(self, instance):
        return instance.muvis_id.resolution
    resolution.short_description = "Resolution"

    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class MuvisBugAddInline(admin.StackedInline):
    verbose_name = "Related Muvis bug"
    verbose_name_plural = "Related Muvis bugs"
    model=ProjectMuvisMapping
    max_rows = 1
    extra = 1
    autocomplete_fields = ["muvis_id"]
    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

class ProjectAttachmentInline(admin.StackedInline):
    verbose_name = "Attachment"
    verbose_name_plural = "Attachments"
    classes = ["collapse"]
    model = ProjectAttachment
    max_rows = 1
    extra = 0
    readonly_fields = ["uploaded", "preview"]
    fields = ["name", "uploaded", "attachment", "description", "preview"]
    def has_change_permission(self, request, obj=None):
        return False

class WatchingUserInline(admin.TabularInline):
    model = Project.watch_list.through
    verbose_name = "Watching user"
    verbose_name_plural = "Watching users"
    max_rows = 0
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_id", "name", "full_title", "pi_link",
        "team_liaison", "affiliation_links", "status")
    search_fields = ["name", "full_title", "id", "pi__name"]
    list_filter = ("status", "team_liaison", "affiliation", "funding")
    save_on_top = True
    readonly_fields = [
        "id", "samples_in_custody", "sample_count", "last_email_sent", "status"
    ]
    fieldsets = [
        ("Project Details", {"fields": [
            "name", "full_title", "id",  "team_liaison", "samples_in_custody", "status",
            "description", "affiliation", "funding", "url", "last_email_sent"]}),
        ("Contact Details", {"fields": ["pi", "contact"]}),
        ("Agreements", {"fields": [
            "collaboration_agreement", "mta_needed", "mta_approved", "mta_reference",
            "ethics_needed", "ethics_approved", "ethics_reference"]}),
        ("Notes", {"fields": ["notes"]}),
    ]
    autocomplete_fields = ["pi", "contact", "affiliation", "funding", "team_liaison"]
    inlines = [
        OtherContactInline,
        MuvisBugLinkInline,
        WatchingUserInline,
        MuvisBugAddInline,
        ProjectAttachmentInline,
        AddProjectStatusInline,
        ProjectStatusInline,
        SampleInline,
        ReportInline
    ]
    actions = [
        "bulk_print_la62",
        "bulk_print_lb68",
        "bulk_contact_print"
    ]

    def bulk_contact_print(self, request, queryset):
        success = True
        for project in queryset:
            success &= print_address_label(project.contact)
        if success:
            messages.success(request, "Label(s) sent for printing.")
        else:
            messages.error(request, "Failed to send label(s) for printing.")
    bulk_contact_print.short_description = "Print contact address labels"

    def bulk_print_lb68(self, request, queryset):
        self.bulk_print(request, queryset, LB68_PRINTER_11354)
    bulk_print_lb68.short_description = "Print labels (LB68)"

    def bulk_print_la62(self, request, queryset):
        self.bulk_print(request, queryset, LA62_PRINTER_11354)
    bulk_print_la62.short_description = "Print labels (LA62)"

    def bulk_print(self, request, queryset, printer):
        success = True
        for project in queryset:
            success &= print_project_label(project, printer_name=printer)
        if success:
            messages.success(request, "Label(s) sent for printing.")
        else:
            messages.error(request, "Failed to send label(s) for printing.")

    def save_formset(self, request, form, formset, change):
        if formset.model == ProjectUpdate:
            instances = formset.save(commit=False)
            for instance in instances:
                if not hasattr(instance, "user"): #if the user isn't already set
                    instance.user = request.user
                instance.save()
                instance.send_update_emails()
        if formset.model == ProjectAttachment:
            instances = formset.save(commit=False)
            for instance in instances:
                if not hasattr(instance, "uploaded_by"):
                    instance.uploaded_by = request.user
                instance.save()
        else:
            formset.save()

    def save_model(self, request, obj, form, change):
        if obj.pk:
            new_item = False
        else:
            new_item = True
        super().save_model(request, obj, form, change)
        if new_item:
            update = ProjectUpdate()
            update.project = obj
            update.user = request.user
            update.last_action_date = timezone.now()
            update.last_action = "Project created"
            update.clean()
            update.save()

    def get_form(self, request, obj=None, **kwargs): #pylint: disable=arguments-differ
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["name"].widget.attrs["style"] = "width:60em;"
        form.base_fields["full_title"].widget.attrs["style"] = "width:60em;"
        return form

    def response_change(self, request, obj):
        if "_report" in request.POST:
            context = {}
            context["opts"] = Project._meta
            context["is_popup"] = False
            context["project"] = obj
            context["has_permission"] = True
            context["site_header"] = self.admin_site.site_header

            return render(
                request,
                "admin/projects/project/report.html",
                context=context)
        printer = None
        if "_print_label_la62" in request.POST:
            printer = LA62_PRINTER_11354
        if "_print_label_lb68" in request.POST:
            printer = LB68_PRINTER_11354
        if printer:
            if print_project_label(obj, printer_name=printer):
                messages.success(request, "Label sent for printing.")
            else:
                messages.error(request, "Failed to send label for printing.")
            return HttpResponseRedirect(reverse('admin:projects_project_change', args=[obj.id]))
        if "_print_contact_label" in request.POST:
            if print_address_label(obj.contact):
                messages.success(request, "Label sent for printing.")
            else:
                messages.error(request, "Failed to send label for printing.")
            return HttpResponseRedirect(reverse('admin:projects_project_change', args=[obj.id]))

        return super().response_change(request, obj)


class PrimaryContactProjectInline(admin.TabularInline):
    verbose_name = "Project as primary contact"
    verbose_name_plural = "Projects as primary contact"
    model = Project
    extra = 0
    fk_name = "contact"
    can_delete = False
    max_num = 0
    fields = ["name_link", "full_title", "pi", "contact_link", "other_contact_links", "funding"]
    readonly_fields = [
        "name_link", "full_title", "pi", "contact_link", "other_contact_links", "funding"
    ]
    exclude = [
        "description", "notes", "affiliation", "collaboration_agreement", "ethics_needed",
        "ethics_approved", "ethics_reference", "mta_needed", "mta_approved", "mta_reference",
        "url", "mta_recieved"
    ]
    show_change_link = True


class PiProjectInline(admin.TabularInline):
    verbose_name = "Project as principal investigator"
    verbose_name_plural = "Projects as principal investigator"
    model = Project
    extra = 0
    fields = ["name_link", "full_title", "contact_link", "other_contact_links", "funding"]
    readonly_fields = ["name_link", "full_title", "contact_link", "other_contact_links", "funding"]
    exclude = [
        "description", "notes", "affiliation", "collaboration_agreement", "ethics_needed",
        "ethics_approved", "ethics_reference", "mta_needed", "mta_approved", "mta_reference",
        "url", "mta_recieved"
    ]
    can_delete = False
    max_num = 0
    fk_name = "pi"
    show_change_link = True

class OtherContactProjectInline(admin.TabularInline):
    verbose_name = "Other project"
    verbose_name_plural = "Other projects"
    model = Project.other_contacts.through
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ["project_name_link", "project_title", "pi_link", "primary_contact_link"]
    fields = ["project_name_link", "project_title", "pi_link", "primary_contact_link"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
        Control the layout of the contact admin page
    """
    fieldsets = [
        ("Personal Details", {"fields": [
            "name", "affiliation", "email", "url", "phone", "address"]}),
        ("Notes", {"fields": ["notes"]})
    ]
    list_display = ("name", "email", "phone", "notes")
    search_fields = ["name"]
    ordering = ["name"]
    autocomplete_fields = ["affiliation"]
    inlines = [
        PiProjectInline,
        PrimaryContactProjectInline,
        OtherContactProjectInline
    ]
    actions = [
        "bulk_print",
        "generate_csv",
        "view_details",
    ]

    def view_details(self, request, queryset):
        context = {}
        context["opts"] = Contact._meta
        context["is_popup"] = False
        context["has_permission"] = True
        context["site_header"] = self.admin_site.site_header
        context["contacts"] = []
        for contact in queryset:
            details = {}
            if contact.email:
                details["name"] = contact.name
                details["email"] = contact.email
                context["contacts"].append(details)
        return render(request, "admin/projects/contact_list.html", context=context)
    view_details.short_description =  "View basic details"

    def generate_csv(self, request, queryset):
        return contact_details_csv(queryset)
    generate_csv.short_description = "Generate CSV dump"

    def bulk_print(self, request, queryset):
        success = True
        for contact in queryset:
            success &= print_address_label(contact)
        if success:
            messages.success(request, "Label(s) sent for printing.")
        else:
            messages.error(request, "Failed to send label(s) for printing.")
    bulk_print.short_description = "Print address labels"

    def response_change(self, request, obj):
        if "_print_label" in request.POST:
            if print_address_label(obj):
                messages.success(request, "Label sent for printing.")
            else:
                messages.error(request, "Failed to send label for printing.")
            return HttpResponseRedirect(reverse('admin:projects_contact_change', args=[obj.id]))
        return super().response_change(request, obj)


class ContactInstitutionInline(admin.TabularInline):
    verbose_name = "People"
    verbose_name_plural = "People"
    extra = 0
    can_delete = False
    max_num = 0
    model = Contact.affiliation.through
    def has_change_permission(self, request, obj=None):
        return False

class ProjectInstitutionInline(admin.TabularInline):
    verbose_name = "Project"
    verbose_name_plural = "Projects"
    extra = 0
    can_delete = False
    max_num = 0
    model = Project.affiliation.through
    def has_change_permission(self, request, obj=None):
        return None

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "url"]
    ordering = ["name"]
    search_fields = ["name"]
    inlines = [
        ContactInstitutionInline,
        ProjectInstitutionInline
    ]

class ProjectFunderInline(admin.TabularInline):
    verbose_name = "Project"
    verbose_name_plural = "Projects"
    extra = 0
    can_delete = False
    max_num = 0
    model = Project.funding.through
    def has_change_permission(self, request, obj=None):
        return None

@admin.register(Funder)
class FunderAdmin(admin.ModelAdmin):
    list_display = ["name", "url"]
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [
        ProjectFunderInline
    ]

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = [
        "name", "description", "inactive_period",
        "notification_period", "escalation_period"]
    ordering = ["name"]

@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = [
        "project", "status", "last_updated", "last_action", "next_action",
        "next_action_deadline", "next_action_status"]
    list_filter = ["project", "status", "next_action_status"]
    ordering = ["project", "last_updated"]
    fieldsets = [
        ("Overview", {"fields": ["project", "project_link", "status", "user", "notes"]}),
        ("Last Action", {"fields": ["last_action_date", "last_action"]}),
        ("Next Action", {"fields": ["next_action_deadline", "next_action", "next_action_status"]})
    ]
    autocomplete_fields = ["project"]
    def get_readonly_fields(self, request, obj=None):
        always = ["user", "project_link"]
        if obj:
            return always + [
                "project", "status", "user", "notes", "last_action_date", "last_action",
                "next_action_deadline", "next_action"
            ]
        return always

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()
        obj.send_update_emails()

@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ["project"]
    readonly_fields = ["uploaded", "preview"]
    fields = ["project", "name", "uploaded", "attachment", "description", "preview",]
    list_display = ["project", "name", "uploaded"]
    ordering = ["project", "name"]
    list_filter = ["project"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        obj.save()
