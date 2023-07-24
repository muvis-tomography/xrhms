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

    CLI entry point for sending emails

"""
import logging
import os
from sys import stderr, exit
from argparse import ArgumentParser

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()

from email_processor import EmailProcessor

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
    EMAIL_TYPE = PARSER.add_mutually_exclusive_group()
    EMAIL_TYPE.add_argument(
        "-w",
        "--weekly",
        action="store_true",
        help="Send the weekly project discussion email"
    )
    EMAIL_TYPE.add_argument(
        "-c",
        "--chase",
        action="store_true",
        help="Send the project chase emails")
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.INFO
    if ARGS.quiet:
        LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        LOG_LEVEL = logging.DEBUG
    if not (ARGS.weekly or ARGS.chase):
        print("UNKNOWN: Must define  one type of email to send")
        exit(3)
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    CONSOLE_HANDLER = logging.StreamHandler(stderr)
    CONSOLE_HANDLER.setLevel(LOG_LEVEL)
    CONSOLE_HANDLER.setFormatter(FORMATTER)
    HANDLERS = [CONSOLE_HANDLER]
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=HANDLERS)
    EMAILER = EmailProcessor(LOG_LEVEL)
    try:
        if ARGS.weekly:
            SENT = EMAILER.send_weekly_email()
            print("OK: Sent {} weekly meeting email(s)".format(SENT))
            exit(0)
        elif ARGS.chase:
            SENT = EMAILER.send_project_inactive_emails()
            print("OK: Sent {} project chase email(s)".format(SENT))
            exit(0)
    except Exception as err:
        stderr.write(str(err))
        print("CRITICAL: An error occured, see error output")
        exit(2)
    print("CRITICAL: Got to unexpected path through the code")
    exit(2)
