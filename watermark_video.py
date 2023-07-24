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

    Use the utilities to apply a watermark to a video
"""

import logging
from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime
import sys
from os import mkdir
from shutil import copyfile
from xrh_utils import apply_overlay

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Apply the image given to the video")
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
        action='version',
        version='%(prog)s 0.1')
    PARSER.add_argument(
        "video",
        action="store",
        help="The video to watermark")
    PARSER.add_argument(
        "image",
        action="store",
        help="Image to overlay")
    X_POS = PARSER.add_mutually_exclusive_group()
    X_POS.add_argument(
        "-l",
        "--left",
        action="store_true",
        default=True,
        help="Position the watermark relative to the left edge")
    X_POS.add_argument(
        "-r",
        "--right",
        action="store_true",
        default=False,
        help="Position the watermark relative to the right edge")
    Y_POS = PARSER.add_mutually_exclusive_group()
    Y_POS.add_argument(
        "-t",
        "--top",
        action="store_true",
        default=True,
        help="Position the watermark relative to the top edge")
    Y_POS.add_argument(
        "-b",
        "--bottom",
        action="store_true",
        default=False,
        help="Position the watermark relative to the bottom edge")
    PARSER.add_argument(
        "--margin",
        type=int,
        help="How many pixels between edge of image and edge of video",
        default=25)
    PARSER.add_argument(
        "--transparency",
        type=float,
        default=0.5,
        help="How transparent to make the overlay")
    PARSER.add_argument(
        "--image-height",
        type=float,
        default=0.1,
        help="How big should the watermark be relative to the video")
    PARSER.add_argument(
        "-d",
        "--directory",
        action="store",
        default="/tmp",
        help="Where to put the output")
    PARSER.add_argument(
        "--crf",
        type=int,
        action="store",
        default=15,
        help="FFMPEG quality to use")
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.INFO
    if ARGS.quiet:
        LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        LOG_LEVEL = logging.DEBUG
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    CONSOLE_HANDLER = logging.StreamHandler(sys.stdout)
    CONSOLE_HANDLER.setLevel(LOG_LEVEL)
    CONSOLE_HANDLER.setFormatter(FORMATTER)
    HANDLERS = [CONSOLE_HANDLER]
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=HANDLERS)
    logging.getLogger("pyvips.vobject").setLevel(logging.ERROR)
    logging.getLogger("pyvips.voperation").setLevel(logging.ERROR)
    VIDEO = Path(ARGS.video)
    IMAGE = Path(ARGS.image)
    try:
        (TEMP_DIR, OUTPUT) = apply_overlay(
            VIDEO,
            IMAGE,
            not ARGS.bottom,
            not ARGS.right,
            ARGS.transparency,
            ARGS.image_height,
            ARGS.margin,
            ARGS.crf)
        DIR = Path(
            ARGS.directory,
            "{}-watermarked".format(datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")))
        mkdir(str(DIR))
        copyfile(str(Path(TEMP_DIR.name, OUTPUT)), str(Path(DIR, OUTPUT)))
    except (ValueError, FileNotFoundError) as err:
        print(err)
        sys.exit(1)
