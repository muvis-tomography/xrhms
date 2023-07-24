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

    Copy the datasets to the user accessible share

"""

import logging
from argparse import ArgumentParser
from sys import stderr, exit
from dataset_processor import DatasetProcessor

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Copy the datasets to the user accessible folder")
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
        "-c",
        "--copies",
        action="store_true",
        help="Process any new copies in the queue")
    PARSER.add_argument(
        "-d",
        "--deletions",
        action="store_true",
        help="Process any eligible deletions")
    PARSER.add_argument(
        "-t",
        "--threshold",
        type=int,
        help="Only process deletions if free space is below this threshold")
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
    logging.getLogger('sh.stream_bufferer').setLevel(logging.WARN)
    logging.getLogger('sh.command.process.streamreader').setLevel(logging.WARN)
    logging.getLogger('sh.command').setLevel(logging.WARN)
    logging.getLogger('sh.streamreader').setLevel(logging.WARN)
    LOGGER = logging.getLogger("User dataset copier")
    PROCESSOR = DatasetProcessor(LOG_LEVEL)
    if not (ARGS.copies or ARGS.deletions):
        PARSER.error("Must specify either copies or deletions")
    COPIED = 0
    COPY_TOTAL = 0
    if ARGS.copies:
        (COPIED, COPY_TOTAL) = PROCESSOR.process_copy_queue()
        if COPY_TOTAL:
            COPIED_PERCENT = COPIED / COPY_TOTAL * 100
        else:
            COPIED_PERCENT = 100
        LOGGER.info("Copied %d/%d items (%.0f%%)", COPIED, COPY_TOTAL, COPIED_PERCENT)
    DELETED = 0
    DELETED_TOTAL = 0
    if ARGS.deletions:
        if ARGS.threshold:
            LOGGER.debug("Checking threshold")
            if PROCESSOR.usage_threshold_exceeded(ARGS.threshold):
                LOGGER.debug("Threshold breached")
                (DELETED, DELETED_TOTAL)  = PROCESSOR.cleanup_user_space()
            else:
                LOGGER.debug("Threshold OK")
        else:
            (DELETED, DELETED_TOTAL)  = PROCESSOR.cleanup_user_space()
        if DELETED_TOTAL:
            DELETED_PERCENT = DELETED / DELETED_TOTAL * 100
        else:
            DELETED_PERCENT = 100
        LOGGER.info("Deleted %d/%d items (%.0f%%)",DELETED, DELETED_TOTAL, DELETED_PERCENT)
    TOTAL_OK = DELETED + COPIED
    TOTAL_ATTEMPTED = COPY_TOTAL + DELETED_TOTAL
    if TOTAL_ATTEMPTED:
        TOTAL_PERCENT = TOTAL_OK / TOTAL_ATTEMPTED * 100
    else:
        TOTAL_PERCENT = 100
    if TOTAL_PERCENT == 100:
        print("OK: Copied: {} Deleted: {} Overall: 100%".format(COPIED, DELETED))
        exit(0)
    if TOTAL_OK == 0:
        print("CRITICAL: 0 actions succeeded")
        exit(2)
    print(
        "WARNING: Only {}/{} {}% actions succeeded".format(
            TOTAL_OK, TOTAL_ATTEMPTED, TOTAL_PERCENT))
exit(3)
