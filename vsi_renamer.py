#!/opt/xrhms-venv/xrhms-env/bin/python3
#pylint: disable=missing-function-docstring,missing-class-docstring
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

    Rename VSI files to a valid XRH name

"""

import logging
from pathlib import Path
import shutil
from argparse import ArgumentParser
from sys import stdout
from dataset_name_validator import DatasetNameValidator

class VSIRenamer():


    def __init__(self, log_level=logging.WARNING):
        self._logger = logging.getLogger("VSI renamer")
        self._logger.setLevel(log_level)

    def rename_file(self, old_name, new_name, force=False):
        if not isinstance(old_name, Path):
            raise ValueError("old_name must be a path")
        if not isinstance(new_name, Path):
            raise ValueError("new_name must be a path")
        if not self.validate_file(old_name):
            self._logger.error("Unable to validate original file")
            raise ValueError("Unable to validate original file")
        if force:
            self._logger.warning("Forcing move so not validating new name")
        else:
            validator = DatasetNameValidator(self._logger.level)
            if not validator.validate_name(new_name.name):
                self._logger.error("New name is invalid")
                raise ValueError("New name is invalid")
        old_dir = self.generate_dir_name(old_name)
        new_dir = self.generate_dir_name(new_name)
        new_vsi_file = Path(old_name.parent, "{}.vsi".format(new_name))
        if new_dir.exists():
            self._logger.error("New directory already exists")
            raise IOError("Unable to create new directory - it exists")
        if new_vsi_file.exists():
            self._logger.errror("New file already exists")
            raise IOError("New VSI file already exists")
        shutil.move(str(old_name), str(new_vsi_file))
        shutil.move(str(old_dir), str(new_dir))
        if not self.validate_file(new_vsi_file):
            raise ValueError("Unable to validate new file")


    def generate_dir_name(self, vsi_name):
        dir_name = Path(vsi_name.parent, "_{}_".format(vsi_name.stem))
        self._logger.debug("Dir name: %s", dir_name)
        return dir_name

    def validate_file(self, name):
        self._logger.debug("Extension: %s", name.suffix)
        if name.suffix != ".vsi":
            self._logger.error("Not a VSI file")
            return False
        if not name.exists():
            self._logger.error("File doesn't exist")
            return False
        dir_path = self.generate_dir_name(name)
        if not dir_path.exists():
            self._logger.error("Required directory doesn't exist")
            return False
        return True

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Change a VSI filename to match the expected schema")
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
        "old",
        type=str,
        action="store",
        help="VSI file to rename")
    PARSER.add_argument(
        "new",
        type=str,
        action="store",
        help="New filename")
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
    RENAMER = VSIRenamer(LOG_LEVEL)
    RENAMER.rename_file(Path(ARGS.old), Path(ARGS.new))
