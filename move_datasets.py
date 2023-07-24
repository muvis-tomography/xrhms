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

    Move the tree(s) specified to the destination
"""

import logging
from argparse import ArgumentParser
from sys import stdout, exit
from pathlib import Path
from dataset_processor import DatasetProcessor

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
        "-s",
        "--source",
        nargs="+",
        help="The directory to move")
    PARSER.add_argument(
        "-d",
        "--destination",
        action="store",
        help="Where to move the directories to")
    PARSER.add_argument(
        "-p",
        "--process",
        action="store_true",
        dest="process_queue",
        help="Process queue")
    PARSER.add_argument(
        "-c",
        "--count",
        type=int,
        default=None,
        help="How many items in the queue to process",
        action="store")
    ARGS = PARSER.parse_args()
    if ARGS.process_queue and (bool(ARGS.source) or bool(ARGS.destination)):
        PARSER.error("If specifying process, CANNOT specify source or destination")
    if bool(ARGS.source) != bool(ARGS.destination):
        PARSER.error("Must specify either both source and destination or neither")
    if not (ARGS.process_queue or bool(ARGS.source)):
        PARSER.error("Must specify either process or a source and destination")
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
    logging.getLogger('sh.stream_bufferer').setLevel(logging.WARN)
    logging.getLogger('sh.command.process.streamreader').setLevel(logging.WARN)
    logging.getLogger('sh.command').setLevel(logging.WARN)
    logging.getLogger('sh.streamreader').setLevel(logging.WARN)
    LOGGER = logging.getLogger("Dataset Mover")
    PROCESSOR = DatasetProcessor(LOG_LEVEL)
    if ARGS.process_queue:
        PROCESSOR.process_move_queue(ARGS.count)
    else:
        LOGGER.info("%d sources to move", len(ARGS.source))
        DEST = Path(ARGS.destination)
        for SOURCE in ARGS.source:
            PROCESSOR.move_subtree(Path(SOURCE), DEST)
    COUNT = PROCESSOR.count_moving()
    if COUNT > 0:
        print(f"ERROR: {COUNT} files still marked as moving")
        exit(2)
