#!/opt/xrhms-venv/xrhms-env/bin/python
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

    Pull data from the muvis database and populate the relevent tables
"""
import os
import logging
from sys import stdout

from argparse import ArgumentParser
import urllib.request
import json

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()

from muvis.models import BugzillaStatus, BugzillaResolution, MuvisBug
class MuvisImporter():
    """
        Class to handle the importing of muvis data into the system
    """

    def __init__(self, url, timeout=10, log_level=logging.WARN):
        """
            Setup the class
        """
        self._logger = logging.getLogger("MuvisImporter")
        self._logger.setLevel = log_level
        self.url = url
        self._logger.info("URL set to %s", self.url)
        self.timeout = float(timeout)
        self._logger.info("Timeout set to %f", self.timeout)

    def update(self):
        """
            Perform the update
        """
        total_bug_count = 0
        update_bug_count = 0
        new_bug_count = 0
        new_resolution_count = 0
        new_status_count = 0
        json_data = self._get_json()
        for bug in json_data:
            total_bug_count += 1
            bug_id = bug["bug_id"]
            bug_status = bug["bug_status"]
            bug_resolution = bug["resolution"]
            bug_desc = bug["short_desc"]
            if MuvisBug.objects.filter(pk=bug_id).exists():
                self._logger.debug("Bug %d already in database", bug_id)
                bug_obj = MuvisBug.objects.get(pk=bug_id)
                if bug_resolution == "":
                    bug_resolution = None
                if (
                        str(bug_obj.title) == bug_desc and
                        str(bug_obj.status) == bug_status and
                        str(bug_obj.resolution) == str(bug_resolution)):
                    #It hasn't changed so no need to go any further
                    self._logger.debug("Bug %d is unchanged", bug_id)
                    continue
            else:
                bug_obj = None
            if BugzillaStatus.objects.filter(name=bug_status).exists():
                self._logger.debug("Using existing status object")
                bug_status_obj = BugzillaStatus.objects.get(name=bug_status)
            else:
                self._logger.info("Creating a new status type: %s", bug_status)
                new_status_count += 1
                bug_status_obj = self._create_status(bug_status)
            if bug_resolution is None:
                self._logger.debug("No resolution set")
                bug_resolution_obj = None
            else:
                if BugzillaResolution.objects.filter(name=bug_resolution).exists():
                    self._logger.debug("Using existing resolution")
                    bug_resolution_obj = BugzillaResolution.objects.get(name=bug_resolution)
                else:
                    self._logger.info("Creating new resolution: %s", bug_resolution)
                    new_resolution_count += 1
                    bug_resolution_obj = self._create_resolution(bug_resolution)
            if bug_obj is not None:
                update_bug_count += 1
                self._update_bug(bug_obj, bug_desc, bug_status_obj, bug_resolution_obj)
            else:
                self._logger.info("Adding new bug ID: %s", bug_id)
                new_bug_count += 1
                self._create_bug(bug_id, bug_desc, bug_status_obj, bug_resolution_obj)
        self._logger.info("New bugs:%d", new_bug_count)
        self._logger.info("Updated bugs:%d", update_bug_count)
        self._logger.info("New statuses:%d", new_status_count)
        self._logger.info("New resolutions:%d", new_resolution_count)
        self._logger.info("Total bugs:%d", total_bug_count)

    def _get_json(self):
        """
            Get the json from the server
        """
        self._logger.info("Fetching data from: %s", self.url)
        page = urllib.request.urlopen(self.url, timeout=self.timeout)
        data = json.loads(page.read().decode())
        self._logger.info("Fetched %d records", len(data))
        return data

    def _create_status(self, bug_status):
        """
            Create a new bugzilla status
        """
        status = BugzillaStatus(name=bug_status)
        status.save()
        self._logger.debug("Status %s creates (%d)", bug_status, status.id)
        return status

    def _create_resolution(self, bug_resolution):
        """
            create a new bugzilla resolution
        """
        resolution = BugzillaResolution(name=bug_resolution)
        resolution.save()
        self._logger.debug("Resolution %s created (%d)", bug_resolution, resolution.id)
        return resolution

    def _update_bug(self, bug, bug_desc, bug_status, bug_resolution=None):
        """
            Update an existing bug
            :params
                bug: The object of the existing bug
                bug_desc: string description
                bug_status: The object of the new status
                bug_resolution: The object of the new resolution
        """
        bug.title = bug_desc
        bug.status = bug_status
        bug.resolution = bug_resolution
        bug.save()
        self._logger.debug("Bug %s updated", bug.muvis_id)

    def _create_bug(self, bug_id, bug_desc, status, resolution=None):
        """
            Create a new bug
            :params
                bug_id: The id of the new bug to create
                bug_desc: string description
                bug_status: The object of the new status
                bug_resolution: The object of the new resolution
        """
        bug = MuvisBug(
            muvis_id=bug_id,
            title=bug_desc,
            status=status,
            resolution=resolution)
        bug.save()
        self._logger.debug("Bug %s created", bug_id)

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Pull bug data across from bugzilla")
    PARSER.add_argument(
        "url",
        action="store",
        help="The URL to pull the data from")
    PARSER.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10,
        action="store",
        help="How long to wait for a response from the server")
    LOGGING_OUTPUT = PARSER.add_mutually_exclusive_group()
    LOGGING_OUTPUT.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress most ouput")
    LOGGING_OUTPUT.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Maximum verbosity output on command line")
    ARGS = PARSER.parse_args()
    URL = ARGS.url
    TIMEOUT = ARGS.timeout
    LOG_LEVEL = logging.WARN
    if ARGS.quiet:
        LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        LOG_LEVEL = logging.DEBUG
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    CONSOLE_HANDLER = logging.StreamHandler(stdout)
    CONSOLE_HANDLER.setLevel(LOG_LEVEL)
    CONSOLE_HANDLER.setFormatter(FORMATTER)
    HANDLERS = [CONSOLE_HANDLER]
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=HANDLERS)
    MUVIS_UPDATER = MuvisImporter(URL, TIMEOUT, LOG_LEVEL)
    MUVIS_UPDATER.update()
