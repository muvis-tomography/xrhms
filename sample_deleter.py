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
    
    Delete the speified XRH ID from the system completely

"""
import logging
from argparse import ArgumentParser
from sys import stderr
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from samples.models import Sample

class SampleDeleter():
    """
        Will work out what the effects will be and ask for confirmation
    """

    def __init__(self, xrh_id, log_level=logging.WARN):
        """
            Setup the class
            :param string xrh_id: The object to delete
            :param int log_level: default: WARNING how much debug output to produce
        """
        self._xrh_id = xrh_id
        self._prepared = False
        self._processed = False
        self._logger = logging.getLogger("SampleDeleter")
        self._logger.setLevel(log_level)
        self._logger.info("Sample deleter created with XRH-ID = %s", self._xrh_id)
        self._sample = None
        self._attachments = None
        self._location_mappings = None
        self._muvis_mappings = None


    def _list_actions(self):
        """
            Prepare a string saying what this action will do
        """
        if not self._prepared:
            self._logger.error("Cannot list actions before preparing")
            return ""
        if self._sample.original_id:
            orig_id_str = "({}) ".format(self._sample.original_id)
        else:
            orig_id_str = ""
        output = "Deleting sample {} {}will delete the following items:\n".format(
            self._xrh_id, orig_id_str)
        output += "{} Sample Attachments\n".format(self._attachments.count())
        for attachment in self._attachments.all():
            output += "\t{}\n".format(attachment.name)
        output += "{} Location history entries\n".format(self._location_mappings.count())
        output += "{} Links to muvis bugs\n".format(self._muvis_mappings.count())
        for bug_map in self._muvis_mappings.all():
            output += "\t{}\n".format(bug_map.bug.title)
        return output

    def prepare(self): #pylint: disable=too-many-return-statements
        """
            Work out what needs to be done
        """
        if self._prepared:
            self._logger.error("Already prepared the operation")
            return (True, self._list_actions())
        if self._processed:
            self._logger.error("Already deleted this item")
            return (False, None)
        try:
            self._sample = Sample.objects.get(full_xrh_id=self._xrh_id)
        except ObjectDoesNotExist:
            self._logger.error("Unable to find that sample")
            return (False, "Unable to find that sample")
        if self._sample == Sample.objects.latest("xrh_id_number"):
            self._logger.error("Cannot delete the latest sample in the database")
            return (False, "Cannot delete the latest sample in the database")
        scan_count = self._sample.nikonctscan_set.count()
        if scan_count != 0:
            self._logger.error("Sample has scans attached cannot delete")
            return (
                False,
                "Sample has scans attached.  If you really want to delete please reassign them")
        process_count = self._sample.process_set.count()
        if process_count != 0:
            self._logger.error("Sample has been processed, cannot delete")
            return (False, "Sample has been processed, and cannot be deleted")
        self._attachments = self._sample.sampleattachment_set
        self._logger.debug("Attachments found: %d", self._attachments.count())
        self._location_mappings = self._sample.samplelocationmapping_set
        self._logger.debug("Location history entries found: %d", self._location_mappings.count())
        self._muvis_mappings = self._sample.samplemuvismapping_set
        self._logger.debug("Links to Muvis bugs found: %d", self._muvis_mappings.count())
        self._prepared = True
        self._logger.info("Prepared to delete sample with XRH-ID %s", self._xrh_id)
        return (True, self._list_actions())

    def delete(self, really=False):
        """
            Actually perform the deletion
        """
        if not self._prepared:
            self._logger.error("Must have prepared first")
            return False
        if self._processed:
            self._logger.error("Already deleted")
            return False
        if not really:
            self._logger.error("Safety check failed")
            return False
        self._logger.debug("Validation passed")
        with transaction.atomic():
            self._logger.debug("Deleting location history")
            for location in self._location_mappings.all():
                location.delete()
            self._logger.debug("Deleting attachments")
            for attachment in self._attachments.all():
                attachment.delete()
            self._logger.debug("Deleteing muvis bug mappings")
            for bug_map in self._muvis_mappings.all():
                bug_map.delete()
            self._logger.debug("Deleting sample")
            self._sample.delete()
        return True

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Delete the specified sample")
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
    PARSER.add_argument(
        "sample",
        action="store",
        help="The XRH ID of the sample to be deleted")
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.WARN
    if ARGS.quiet:
        LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        LOG_LEVEL = logging.DEBUG
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    CONSOLE_HANDLER = logging.StreamHandler(stderr)
    CONSOLE_HANDLER.setLevel(LOG_LEVEL)
    CONSOLE_HANDLER.setFormatter(FORMATTER)
    HANDLERS = [CONSOLE_HANDLER]
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=HANDLERS)
    DELETER = SampleDeleter(ARGS.sample, LOG_LEVEL)
    READY, OUTPUT = DELETER.prepare()
    if READY:
        print(OUTPUT)
        RESPONSE = input("Proceed (y/N)")
        if RESPONSE == "y":
            if DELETER.delete(True):
                print("Sample and associated data deleted")
            else:
                print("Delete encountered an error and rolled back")
        else:
            print("Delete aborted")
    else:
        print("Unable to prepare to delete item")
        print(OUTPUT)
