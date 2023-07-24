#!/usr/bin/env python
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

    Force the generation of a report for debug purposes

"""

from argparse import ArgumentParser
from pathlib import Path
from sys import stdout, exit
from glob import glob
import logging
import shutil
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()

from django.core.exceptions import ObjectDoesNotExist

from samples.reports import generate_report
from samples.models import SampleReport

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Generate a report for the specified report number for testing purposes.")
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
        "report",
        type=int,
        action="store",
        help="The report number to generate")
    PARSER.add_argument(
        "-o",
        "--output",
        action="store",
        dest="directory",
        help="Where to store a copy of generated report for debug purposes")
    PARSER.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Run in debug mode.  Doesn't overwrite DB entry more files in folder. Requires -o")
    ARGS = PARSER.parse_args()
    if ARGS.debug and not ARGS.directory:
        PARSER.error("-d requires -o")
    LOG_LEVEL = logging.INFO
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
    LOGGER = logging.getLogger("Report Generator")
    REPORT_NO = ARGS.report
    try:
        REPORT_SPEC = SampleReport.objects.get(pk=REPORT_NO)
    except ObjectDoesNotExist:
        print("Unable to find report")
        exit(1)
    TEMP_DIR = generate_report(REPORT_SPEC, force=True, debug=ARGS.debug)
    if ARGS.directory:
        OUTPUT_DIR = Path(ARGS.directory, "report-{}".format(REPORT_NO))
        LOGGER.debug("Saving files to %s", OUTPUT_DIR)
        if OUTPUT_DIR.exists():
            LOGGER.debug("Output dir already exists")
            for F_NAME in glob(str(Path(OUTPUT_DIR, "*"))):
                LOGGER.warning("Deleting file %s", F_NAME)
                os.remove(F_NAME)
        else:
            OUTPUT_DIR.mkdir()
        for F_NAME in glob(str(Path(TEMP_DIR.name, "*"))):
            LOGGER.debug("Copying file: %s", Path(F_NAME).name)
            shutil.copy(F_NAME, OUTPUT_DIR)
