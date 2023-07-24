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

    Commandline script to scan a directory.
    If a .xtekct or .xtekhelixct file is found then it is processed.
    If it's a new file then it is added into the database and where possible metadata generated
    If it already exists then the checksum is checked to see if there have been any changes
"""

import logging
from sys import stdout, exit
from argparse import ArgumentParser
from pathlib import Path
from dataset_processor import DatasetProcessor


if __name__ == "__main__":
    PARSER = ArgumentParser(
        description=(
            "Process datasets in specified directory." +
            "Checks they are upto date if already recorded, otherwise adds into dataset"))
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
        "directory",
        action="store",
        help="The directory to scan for datasets")
    PARSER.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1")
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
    PROCESSOR = DatasetProcessor(LOG_LEVEL)
    if not PROCESSOR.process_directory(Path(ARGS.directory)):
        print("Errors occured during processing")
        exit(1)
