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

    Produce reports for all entries that need it
"""

from argparse import ArgumentParser
from sys import stderr, exit
import logging
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()


from samples.reports import generate_all_reports

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Generate a report for all reports that need its.")
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
        "-o",
        "--overwrite",
        action="store_true",
        help="Reprocesses all reports. Requires -a")
    PARSER.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Process all records, even the previous processd ones. Requires -o")
    ARGS = PARSER.parse_args()
    if ARGS.all and not ARGS.overwrite:
        PARSER.error("-a requires -o")
    LOG_LEVEL = logging.INFO
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
    LOGGER = logging.getLogger("Report Generator - all")
    (SUCCESS, TOTAL) = generate_all_reports(ARGS.all and ARGS.overwrite)
    if SUCCESS == TOTAL:
        print("OK: Generated {} reports".format(SUCCESS))
    elif TOTAL < 0:
        print("CRITICAL: Unable to run")
        exit(2)
    elif SUCCESS == 0 and TOTAL != 0:
        print("CRITICAL: Failed to generate ANY reports {} attempted".format(TOTAL))
        exit(2)
    elif SUCCESS < TOTAL:
        print("WARNING: Generated {}/{} ({}%) reports".format(
            SUCCESS, TOTAL, int(SUCCESS/TOTAL)))
        exit(1)
    else:
        print("CRITICAL: Unexpected exit condition")
        exit(2)
