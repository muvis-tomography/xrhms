#!/usr/bin/env python3
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
    
    Handle sending emails out from the xrhms.
"""
import logging

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.timezone import now

import projects.views
import projects.models
class EmailProcessor:
    """
        Class to handle actually sending emails
    """
    def __init__(self, loglevel=logging.WARN):
        """
            Set up logging
            :param int loglevel: default logging.WARNING
        """
        self._logger = logging.getLogger("Email processor")
        self._logger.setLevel = loglevel

    def send_weekly_email(self, version=1):
        """
            Send the weekly pre CWG meeting email
            :param version int: The version of the email to send
            :return int: The number of emails sent
        """
        users = get_user_model().objects.filter(profile__weekly_emails=True)
        self._logger.debug("Sending emails to %d users", len(users))
        text_contents = projects.views.weekly_email(version=version, html=False)
        html_contents = projects.views.weekly_email(version=version, html=True)
        subject = "[XRHMS] weekly project discussion list"
        return self._send_emails(users, subject, text_contents, html_contents)

    def send_watch_list_emails(self, project_update, exclude=[], version=1):
        """
            Send emails out to all users who are watching a project
            :param ProjectUpdate project_update: The update to be communicated
            :param [User] exclude: The list of users to not email
            :param int version: The version of the email to send
            :return int: The number of emails sent
        """
        users = project_update.project.watch_list.all()
        self._logger.debug("Sending watch list emails to %d users", len(users))
        text_contents = projects.views.project_update_email(
            project_update, version=version, html=False)
        html_contents = projects.views.project_update_email(
            project_update, version=version, html=True)
        subject = "[XRHMS] Project {} has been updated".format(str(project_update.project))
        return self._send_emails(users, subject, text_contents, html_contents, exclude)

    def _send_emails(self, users, subject, text_contents, html_contents, exclude=[]):
        """
            Internal function to send emails:
            :param [User] users: The list of users to send the email to
            :param string subject: The subject of the email
            :param string text_contents: Plain text version of the contents
            :param string html_contents: HTML version of the email
            :param [User] exclude: users to avoid sending the email to
        """
        self._logger.info("Sending email to: %r", users)
        self._logger.info("Email subject: %s", subject)
        self._logger.info("Excluding users: %r", exclude)
        sent = 0
        users = list(set(users)) #convert to a set to remove duplicates, then back to a list
        for user in users:
            email_address = user.email
            if user in exclude:
                self._logger.debug("%s excluded from update", user)
                continue
            if not email_address:
                self._logger.warning("No email address found for %s", user)
                continue
            self._logger.debug("Sending email to %s (%s)", user, email_address)
            if send_mail(
                    subject,
                    text_contents,
                    None,
                    [email_address],
                    html_message=html_contents):
                self._logger.debug("Email sent for %s", user)
                sent += 1
        return sent

    def send_project_inactive_emails(self, version=1):
        """
            Send emails when a project has been inactive for a set period (or has overdue tassk)
            Will check all projects that are eligible for notifications
            :param int version: The version of the email to send
            :return int: number of emails sent
        """
        project_list = projects.models.Project.objects.all().exclude(status__notification_period=0)
        #If notification period = 0 then it's not eligible for emails so exclude as early as poss
        self._logger.debug("%d projects to iterate through", len(project_list))
        sent_count = 0
        for project in project_list:
            self._logger.debug("Processing project %d %s", project.pk, str(project))
            liaison = project.team_liaison
            users = []
            if liaison is  None:
                self._logger.warning("No team liaison set")
            elif liaison.email is None:
                self._logger.error("No email address for %s", liaison)
            elif not liaison.profile.project_emails:
                self._logger.info("liaison (%s) has opted out of emails", liaison)
            else:
                users.append(liaison)
                self._logger.debug("Team liaison %s", liaison.username)
            if project.watch_list:
                self._logger.debug("Adding watch list to destination list")
                users.extend(project.watch_list.all())
            self._logger.debug("Sending to: %r", users)
            if not users:
                self._logger.warning("No users to recieve email. Skipping")
                continue
            last_email_sent = project.last_email_sent
            self._logger.debug("Last email sent %s", last_email_sent)
            update = project.get_latest_update()
            self._logger.debug("Status %s from %s", update.status, update.last_updated)
            update_delta = now() - update.last_updated
            self._logger.debug("Update %d days ago", update_delta.days)
            if project.notification_eligible():
                #an email is due if the other thresholds are met
                self._logger.debug("Due to send emails if needed")
                sent_count += self._send_project_chase_email(project, users, version)
            else:
                self._logger.debug("Email sent recently")
        return sent_count

    def _send_project_chase_email(self, project, users, version=1):
        """
            Generate and send the reminder email for a given project
            :param Project project: The project to email about
            :param [Users] users: Who to send the email to
            :param int version: Which version of email to sent
            :return int: The number of emails sen
        """
        project_id = project.pk
        escalated = project.inactive_escalation()
        inactive = project.inactive()
        tasks_overdue = project.has_overdue_tasks()
        self._logger.debug(
            "Inactive: %r, escalated %r, tasks_overdue: %r",
            escalated, inactive, tasks_overdue)
        subject = "[XRHMS] "
        if escalated and tasks_overdue:
            subject += "EXTREMELY INACTIVE project ({}) with OVERDUE TASKS ".format(project_id)
        elif escalated:
            subject += "EXTREMELY INACTIVE project ({}) ".format(project_id)
        elif inactive and tasks_overdue:
            subject += "Inactive project ({}) with overdue tasks ".format(project_id)
        elif inactive:
            subject += "Inactive project ({}) ".format(project_id)
        elif tasks_overdue:
            subject += "Project ({}) with tasks overdue ".format(project_id)
        else:
            return 0
        subject += str(project)
        text_contents = projects.views.project_chase_email(project, version=version, html=False)
        html_contents = projects.views.project_chase_email(project, version=version, html=True)
        sent = self._send_emails(users, subject, text_contents, html_contents)
        if sent:
            project.last_email_sent = now()
            project.save()
        return sent
