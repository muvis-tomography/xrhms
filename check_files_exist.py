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
    
    Runs through all the NikonCTScans in the database and checks the files for them still exist


"""

import logging
from sys import stderr
import sys
from argparse import ArgumentParser

from dataset_processor import DatasetProcessor


if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Check all the scans referred to in the database still exists")
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
    ARGS = PARSER.parse_args()
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
    try:
        PROCESSOR = DatasetProcessor(LOG_LEVEL)
        CHANGED_COUNT = PROCESSOR.check_all_exist()
        if CHANGED_COUNT > 0:
            print("WARNING: {} files don't match database".format(CHANGED_COUNT))
            sys.exit(1)
        elif CHANGED_COUNT < 0:
            print("UNKNOWN: Moving operation in progress unable to run")
            sys.exit(3)
        print("OK: Database and filesystem match")
    except Exception as err: #pylint: disable=broad-except
        print("CRITICAL: An exception occured")
        print(err)
        sys.exit(2)
