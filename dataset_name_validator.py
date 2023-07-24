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
    
"""

import logging
from datetime import datetime
from sys import exit, stdout
from argparse import ArgumentParser
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()

from django.core.exceptions import ObjectDoesNotExist

from muvis.models import MuvisBug
from samples.models.xrh_id import check_digit_ok as validate_check_digit, XrhIdValidationError
from samples.models import Sample
from scans.models import Machine


class DatasetNameValidator():
    """
        Class to make sure that the name given to a dataset fits the required structure
    """

    def __init__(self, log_level=logging.WARNING):
        """
            Setup the validator
        """
        self._logger = logging.getLogger("Dataset name validator")
        self._logger.setLevel(log_level)


    def validate_name(self, name):
        """
            Validate the full name
            :param string name: The name to validate
            :return boolean True if valid
        """
        arr = name.split("_")
        self._logger.info("Name has %d parts", len(arr))
        if len(arr) < 5:
            self._logger.error("Name too short. It must contain atleast 5 sections seperated by _.")
            return False
        self._logger.debug("Date: %s", arr[0])
        self._logger.debug("Machine: %s", arr[1])
        self._logger.debug("Bug ID: %s", arr[2])
        self._logger.debug("Operator: %s", arr[3])
        self._logger.debug("XRH ID: %s", arr[4])
        if len(arr) > 6:
            self._logger.debug("Free text: %s", arr[5:])
        date_valid = self.validate_date(arr[0])
        machine_valid = self.validate_machine(arr[1])
        bug_valid = self.validate_bug(arr[2])
        self._logger.debug("No validation performed for operator")
        xrh_id_valid = self.validate_xrh_id(arr[4])
        return date_valid and machine_valid and bug_valid and xrh_id_valid


    def validate_date(self, date):
        """
            Check the date part of the name
            :param string date
            :return boolean
        """
        self._logger.debug("Validating date is in correct format")
        if len(date) != 8:
            self._logger.error(
                "Date has the wrong number of characters. It should be YYYYMMDD e.g. 20210401")
            return False
        try:
            datetime.strptime(date, "%Y%m%d")
            return True
        except ValueError as err:
            self._logger.error("Date invalid: %s", str(err))
            return False

    def validate_machine(self, machine):
        """
            Check the machine specified exists in the database
            :param string machine
            :return boolean
        """
        self._logger.debug("Validating machine is in database")
        try:
            Machine.objects.get(name=machine)
            return True
        except ObjectDoesNotExist:
            self._logger.error("Unable to find that machine")
            return False

    def validate_bug(self, bug):
        """
            Check the bug specified exists in the database
            :param string bug
            :return boolean
        """
        self._logger.debug("Validating bug is known in database")
        if bug == "XXXX":
            self._logger.warning("Bug deliberately invalid")
            return True
        try:
            bug_id = int(bug)
            MuvisBug.objects.get(pk=bug_id)
            return True
        except ObjectDoesNotExist:
            self._logger.error("Unable to find bug in database")
            return False
        except ValueError:
            self._logger.error("Bug ID is not a number")
            return False

    def validate_xrh_id(self, xrh_id):
        """
            Check the validity of the XRH ID and check it exists in the database
            :param string xrh_id
            :return boolean
        """
        self._logger.debug("Validating XRH ID")
        try:
            validate_check_digit(xrh_id)
            Sample.objects.get(full_xrh_id=xrh_id)
            return True
        except XrhIdValidationError:
            self._logger.error("XRH_ID fails check")
            return False
        except ObjectDoesNotExist:
            self._logger.error("Sample does not exist in database")
            return False


if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Move the datasets specified to the destionation")
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
        "name",
        action="store",
        help="The name to be validated")
    PARSER.add_argument(
        "--version",
        action='version',
        version='%(prog)s 0.1')
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.WARNING
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
    logging.getLogger('sh.stream_bufferer').setLevel(logging.WARN)
    logging.getLogger('sh.command.process.streamreader').setLevel(logging.WARN)
    logging.getLogger('sh.command').setLevel(logging.WARN)
    logging.getLogger('sh.streamreader').setLevel(logging.WARN)
    VALIDATOR = DatasetNameValidator(LOG_LEVEL)
    VALID = VALIDATOR.validate_name(ARGS.name)
    if VALID:
        print("Name is valid")
    else:
        print("Name is invalid")
        exit(1)
