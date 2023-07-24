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

    Check the amount of space left in the google drive
"""

from argparse import ArgumentParser
import subprocess
import sys
from xrh_utils import convert_filesize
CMD = [
    "/opt/xrhms-venv/xrhms-env/bin/python3",
    "/opt/xrhms-venv/xrhms/drive_uploader.py",
    "-v", "--quota"
]

def check_quota(warning, critical):
    """
        Actually check the quota
        :param float warning: The percentage remaining at which to raise a warning
        :param float critical: The percentage remaining at which to be critical
        :return (status, message)
    """
    if warning < 0 or warning > 100:
        raise ValueError("Invalid warning threshold ({:.2f})".format(warning))
    if critical < 0 or critical > 100:
        raise ValueError("Invalid critical threshold ({.2f})".format(critical))
    output = subprocess.run(
        CMD,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if output.returncode != 0:
        return (3, "UNKNOWN: Unable to execute script")
    output_arr = output.stdout.decode("utf-8").split(",")
    print(output.stderr, file=sys.stderr)
    used = int(output_arr[0])
    total = int(output_arr[1])
    percentage_used = float(output_arr[2])
    percentage_remaining = 100 - percentage_used
    space_remaining = total - used
    if percentage_remaining < critical:
        return (
            2, "CRITICAL: {} remaining ({:.1f}%)".format(
                convert_filesize(space_remaining), percentage_remaining))
    if percentage_remaining < warning:
        return (
            1, "WARNING: {} remaining ({:.1f}%)".format(
                convert_filesize(space_remaining), percentage_remaining))
    return (
        0, "OK: {} remaining ({:.1f}%)".format(
            convert_filesize(space_remaining), percentage_remaining))

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Icinga check for quota remaining")
    PARSER.add_argument(
        "--version",
        action='version',
        version='%(prog)s 0.1')
    PARSER.add_argument(
        "-w",
        "--warning",
        type=float,
        help="If less than this percentage space left warn",
        default=20)
    PARSER.add_argument(
        "-c",
        "--critical",
        type=float,
        help="If less than this percentage left it's critical",
        default=10)
    ARGS = PARSER.parse_args()
    STATUS = None
    try:
        (STATUS, MSG) = check_quota(ARGS.warning, ARGS.critical)
        print(MSG)
    except: #pylint: disable=bare-except
        print("UNKNOWN: Unable to query quota")
        sys.exit(3)
    sys.exit(STATUS)
