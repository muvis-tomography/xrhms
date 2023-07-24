#! /opt/xrhms-venv/xrhms-env/bin/python
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


    Add lots of samples to the sample proejct, if IDS available can be passed in via a text file
    with one ID per line`

"""
import os
import logging
from sys import stdout
from argparse import ArgumentParser
from pathlib import Path
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings

from muvis.models import MuvisBug

from projects.models import Project

from samples.models import (
    Condition,
    Location,
    Sample,
    SampleIdPrefix,
    SampleLocationMapping,
    SampleMuvisMapping,
    SampleType,
    Species,
    Tissue
)

from labels.utils import print_sample_label, SAMPLE_LABEL_PRINTERS

class BulkAdder():
    """
        Handles the procesing of the list of samples to add
    """
    def __init__(self, log_level=logging.WARN):
        """
            :param log_level int the logging level to use
        """
        self._logger = logging.getLogger("BulkAdder")
        self._logger.setLevel(log_level)

    def add_samples(
            self, prefix, species, tissue, sample_type, project, bug, location=None, count=0,
            id_file=None, condition=None, printer=None):
        """
            Add a number of samples into the system
            :param SampleIdPrefix prefix
            :param Species species
            :param Tissue tissue
            :param SampleType sample_type
            :param Project project
            :param MuvisBug bug
            :param Location location (Optional)
            :param int count (Optional)
            :param Path id_file (Optional)
            :param Condition (Optional)
            :param string printer (Optional)
            :return int
        """
        if count == 0 and id_file is None:
            raise ValueError(
                "Don't know how many samples to create. Must set either count or id_file")
        if count != 0 and id_file is not None:
            raise ValueError("Cannot set both count and id_file")
        if count != 0:
            for _ in range(0, count):
                self._add_sample(prefix, species, tissue, sample_type, project, bug, location,
                    None, condition, printer)
        else:
            if not id_file.exists():
                raise ValueError("ID file must exist")
            count = 0
            with open(id_file) as id_list:
                for original_id in id_list.readlines():
                    self._add_sample(prefix, species, tissue, sample_type, project, bug,
                        location, original_id=original_id, condition=condition, printer=printer)
                    count += 1
        self._logger.info("Added %d samples", count)
        return count


    def _add_sample(self, prefix, species, tissue, sample_type, project, bug, location=None,
        original_id=None, condition=None, printer=None):
        """
            Add a sample into the system and optionally print a label
            :param SampleIdPrefix prefix
            :param Species species
            :param Tissue tissue
            :param SampleType sample_type
            :param Project project
            :param MuvisBug bug
            :param Location location
            :param int count (Optional)
            :param Path id_file (Optional)
            :param Condition (Optional)
            :param string printer (Optional)
        """
        with transaction.atomic():
            new_sample = Sample(
                original_id=original_id,
                xrh_id_prefix=prefix,
                sample_type=sample_type,
                tissue=tissue,
                species=species,
                condition=condition)
            new_sample.save()
            new_sample.project.add(project)
            user = get_user_model().objects.get(pk=settings.SUPER_USER_ID)
            if location:
                slm = SampleLocationMapping(
                    sample=new_sample,
                    location=location,
                    user=user)
                slm.save()
            smm = SampleMuvisMapping(sample=new_sample, bug=bug)
            smm.save()
            self._logger.debug("Sample ID: %s", new_sample.full_xrh_id)
        if printer:
            print_sample_label(new_sample, printer_name=printer)

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description=("Bulk add samples to the system"))
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
        "--version",
        action="version",
        version="%(prog)s 0.1")
    PARSER.add_argument(
        "--bug",
        required=True,
        type=int,
        help="The muvis bug ID")
    PARSER.add_argument(
        "--condition",
        choices=Condition.objects.all().values_list("name", flat=True),
        help="The condition of the sample(s)")
    PARSER.add_argument(
        "--location",
        choices=Location.objects.all().values_list("name", flat=True),
        help="Where the sample(s) are located")
    PARSER.add_argument(
        "--prefix",
        action="store",
        choices=SampleIdPrefix.objects.all().values_list("prefix", flat=True),
        required=True,
        help="The prefix to use for the sample ID")
    PARSER.add_argument(
        "--project",
        type=int,
        required=True,
        help="The numeric ID of the project")
    PARSER.add_argument(
        "--printer",
        action="store",
        help="Where to print the label(s)",
        choices=SAMPLE_LABEL_PRINTERS.keys())
    PARSER.add_argument(
        "--species",
        action="store",
        choices=Species.objects.all().values_list("name", flat=True),
        required=True,
        help="The species of the sample")
    PARSER.add_argument(
        "--tissue",
        action="store",
        choices=Tissue.objects.all().values_list("name", flat=True),
        required=True,
        help="The tissue type of the samples")
    PARSER.add_argument(
        "--type",
        action="store",
        choices=SampleType.objects.all().values_list("name", flat=True),
        required=True,
        help="The sample type")
    SAMPLE_INPUT = PARSER.add_mutually_exclusive_group()
    SAMPLE_INPUT.add_argument(
        "--count",
        type=int,
        help="How many samples to add")
    SAMPLE_INPUT.add_argument(
        "--id_file",
        help="A text file containing line seperated original IDs")
    ARGS = PARSER.parse_args()
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
    logging.getLogger('sh.stream_bufferer').setLevel(logging.ERROR)
    logging.getLogger('sh.streamreader').setLevel(logging.ERROR)
    logging.getLogger('sh.command').setLevel(logging.ERROR)
    logging.getLogger("pyvips.voperation").setLevel(logging.ERROR)
    logging.getLogger("pyvips.vobject").setLevel(logging.ERROR)
    LOGGER = logging.getLogger("Bulk add argument processor")
    if not (ARGS.count or ARGS.id_file):
        PARSER.error("Must specify either sample count or ID file")
    try:
        BUG = MuvisBug.objects.get(pk=ARGS.bug)
        LOGGER.debug("Bug: %s", BUG.title)
    except ObjectDoesNotExist:
        PARSER.error("Invalid Bug entered")
    try:
        PROJECT = Project.objects.get(pk=ARGS.project)
        LOGGER.debug("Project: %s", PROJECT.name)
    except ObjectDoesNotExist:
        PARSER.error("Invalid Project ID entered")
    TYPE = SampleType.objects.get(name=ARGS.type)
    PREFIX = SampleIdPrefix.objects.get(prefix=ARGS.prefix)
    SPECIES = Species.objects.get(name=ARGS.species)
    TISSUE = Tissue.objects.get(name=ARGS.tissue)
    if ARGS.location:
        LOCATION = Location.objects.get(name=ARGS.location)
    else:
        LOCATION = None
    if ARGS.condition:
        CONDITION = Condition.objects.get(name=ARGS.condition)
    else:
        CONDITION = None
    if ARGS.printer:
        PRINTER = SAMPLE_LABEL_PRINTERS[ARGS.printer]
    else:
        PRINTER = None
    ADDER = BulkAdder(LOG_LEVEL)
    if ARGS.count:
        ADDER.add_samples(PREFIX, SPECIES, TISSUE, TYPE, PROJECT, BUG, LOCATION,
            count=ARGS.count, condition=CONDITION, printer=PRINTER)
    else:
        ADDER.add_samples(PREFIX, SPECIES, TISSUE, TYPE, PROJECT, BUG, LOCATION,
            id_file=Path(ARGS.id_file), condition=CONDITION, printer=PRINTER)
