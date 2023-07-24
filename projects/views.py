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
    
    Custom views for the projects application
"""
import csv
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
import projects.models
# Create your views here.

def weekly_email(version=1, html=True):
    """
        Generate content for the weekly reminder email
        :param int version: Which version of the email to send
        :param bool html: Default = True: HTML or plain text output?
        :return string: email contents
    """
    context = {}
    if version == 1:
        discussion_status = projects.models.ProjectStatus.objects.get(name="Needs team discussion")
        project_list = projects.models.Project.objects.filter(status=discussion_status)
        context["discussion"] = []
        for project in project_list:
            details = {}
            details["name"] = str(project)
            details["url"] = mark_safe("https://{}{}".format(
                settings.ALLOWED_HOSTS[0],
                reverse('admin:projects_project_change', args=[project.pk])))
            context["discussion"].append(details)
        context["liaison"] = []
        needs_liaison = projects.models.Project.objects.filter(
            team_liaison__isnull=True).exclude(status__notification_period=0)
        for project in needs_liaison:
            details = {}
            details["name"] = str(project)
            details["url"] = mark_safe("https://{}{}".format(
                settings.ALLOWED_HOSTS[0],
                reverse('admin:projects_project_change', args=[project.pk])))
            context["liaison"].append(details)
        potentially_escalated_list = projects.models.Project.objects.all().exclude(
            status__notification_period=0)
        context["escalated_projects"] = []
        for project in potentially_escalated_list:
            if not project.inactive_escalation():
                continue
            details = {}
            details["name"] = str(project)
            details["url"] = mark_safe("https://{}{}".format(
                settings.ALLOWED_HOSTS[0],
                reverse('admin:projects_project_change', args=[project.pk])))
            context["escalated_projects"].append(details)
        if html:
            return render_to_string("projects/weekly_email_v1.html", context)
        return render_to_string("projects/weekly_email_v1.txt", context)
    raise ValueError("Invalid version specified")

def project_update_email(project_update, version=1, html=True):
    """
        Generate content for an email whenever a project is updated
        :param ProjectUpdate project_update: The update to email about
        :param int version: Which version of the email to send
        :param bool html: Default = True: HTML or plain text output?
        :return string: email contents
    """
    context = {}
    if version == 1:
        project = project_update.project
        context["project_full_title"] = project.full_title
        context["project_name"] = project.name
        context["project_status"] = project_update.status.name
        context["project_url"] = mark_safe("https://{}{}".format(
            settings.ALLOWED_HOSTS[0],
            reverse('admin:projects_project_change', args=[project.pk])))
        context["updated_by"] = project_update.user.username
        context["updated"] = project_update.last_updated
        context["last_action"] = project_update.last_action
        context["last_action_date"] = project_update.last_action_date
        context["notes"] = project_update.notes
        context["next_action"] = project_update.next_action
        context["next_action_deadline"] = project_update.next_action_deadline
        context["next_action_status"] = project_update.get_next_action_status_display()
        context["update_url"] = mark_safe("https://{}{}".format(
            settings.ALLOWED_HOSTS[0],
            reverse('admin:projects_projectupdate_change', args=[project_update.pk])))
        if html:
            return render_to_string("projects/project_update_email_v1.html", context)
        return render_to_string("projects/project_update_email_v1.txt", context)
    raise ValueError("Invalid version specified")

def project_chase_email(project, version=1, html=True):
    """
        Generate content for an email chasing an inactive project
        :param Project project: The update to email about
        :param int version: Which version of the email to send
        :param bool html: Default = True: HTML or plain text output?
        :return string: email contents
    """
    context = {}
    if version == 1:
        context["project_full_title"] = project.full_title
        context["project_name"] = project.name
        context["project_status"] = project.status
        context["last_updated"] = str(project.get_latest_update().last_updated)
        context["project_url"] = mark_safe("https://{}{}".format(
            settings.ALLOWED_HOSTS[0],
            reverse('admin:projects_project_change', args=[project.pk])))
        context["tasks"] = []
        for task in project.get_overdue_tasks():
            task_details = {}
            task_details["due_date"] = task.next_action_deadline
            task_details["task"] = task.next_action
            task_details["url"] = mark_safe("https://{}{}".format(
            settings.ALLOWED_HOSTS[0],
            reverse('admin:projects_projectstatus_change', args=[task.pk])))

            context["tasks"].append(task_details)
        if html:
            return render_to_string("projects/project_chase_email_v1.html", context)
        return render_to_string("projects/project_chase_email_v1.txt", context)
    raise ValueError("Invalid version specified")

def contact_details_csv(contacts):
    response = HttpResponse(content_type="text\\csv")
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
    csv_writer = csv.writer(response)
    csv_writer.writerow([
        "Name", "Email", "Phone", "address", "Affiliations", "URL"
        ])
    for contact in contacts:
        name = contact.name
        if contact.email:
            email = contact.email
        else:
            email = "-"
        if contact.phone:
            phone = contact.phone
        else:
            phone = "-"
        if contact.address:
            address = contact.address.replace("\r\n", ",")
        else:
            address = "-"
        if contact.url:
            url = contact.url
        else:
            url = "-"
        affiliation_names = []
        for affiliation in contact.affiliation.all():
            affiliation_names.append(affiliation.name)
        affiliation_list = "'{}'".format("','".join(affiliation_names))
        csv_writer.writerow([name, email, phone, address, affiliation_list, url])
    return response
