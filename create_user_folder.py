#!/opt/xrhms-venv/xrhms-env/bin/python3
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

    Standalone script to create a folder for a user and assign it the correct permissions.
    Must be run as root

"""

import logging
from argparse import ArgumentParser
from sys import stderr, exit
from pathlib import Path
import os
import sh
from xrh_utils import validate_user

DEFAULT_FOLDER_PERMISSIONS = 770 # the permissions to create the folder with
DEFAULT_GROUP = "xrh" # the group to use if not specified

class UserFolderManager():
    """
        Class to handle creating folders
    """

    def __init__(self, log_level=logging.WARN):
        """
            Setup the instance
            :param int log_level: The level of verbosity for logging defaults to WARN
        """
        self._logger = logging.getLogger("User folder creater")
        self._logger.setLevel(log_level)
        if os.getuid() != 0:
            self._logger.error("Must be run as root: UID = %d", os.getuid())
            raise ValueError("Must be run as root")

    def create_user_folder(
            self, username, base_folder,
            group=DEFAULT_GROUP,
            permissions=DEFAULT_FOLDER_PERMISSIONS):
        """
            Create the folder for the user and assign it permissions
            :param string username: The name of the folder to create (and the user to assign it to)
            :param string base_folder: Where to create the folder.
            :param string group: The group to assign the folder to. (Optional)
            :param string permissions: the permissions to assign to the folder (Optional)
        """
        self._logger.info("Username: %s", username)
        self._logger.info("Base folder: %s", base_folder)
        base = Path(base_folder)
        if not base.exists():
            self._logger.error("Base folder %s does not exist", base_folder)
            raise ValueError("Base folder {} does not exist".format(base_folder))
        folder_path = Path(base_folder, username)
        self._logger.debug("Folder path: %s", folder_path)
        if folder_path.exists():
            #the folder already exists where it should so just check permissions are ok
            self._logger.info("Folder %s already exists", folder_path)
            self._set_permissions(folder_path, username, group, permissions)
            return
        #The folder doesn't exist
        if not validate_user(username):
            self._logger.error("Username (%s) not found", username)
            raise ValueError("Username ({}) not found".format(username))
        folder_path.mkdir(permissions) # create the folder
        self._set_permissions(folder_path, username, group, permissions)


    def _set_permissions(
            self, folder_path, username,
            group=DEFAULT_GROUP,
            permissions=DEFAULT_FOLDER_PERMISSIONS):
        """
            Set the permissions on the folder
            :param Path folder_path: The object to set the perms on]
            :param string group: The group to assign the folder to. (Optional)
            :param string permissions: the permissions to assign to the folder (Optional)
        """
        self._logger.info("Folder: %s", folder_path)
        self._logger.info("User: %s", username)
        self._logger.info("Group: %s", group)
        self._logger.info("Permissions: %s", permissions)
        if not isinstance(folder_path, Path):
            raise ValueError("folder_path must be a Path object")
        if not validate_user(username):
            raise ValueError("Invalid username")
        sh.chown(username, str(folder_path))
        sh.chmod(permissions, str(folder_path))
        sh.chgrp(group, str(folder_path))

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Create a folder for the specified username")
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
        "username",
        action="store",
        help="The username to create a folder for")
    PARSER.add_argument(
        "folder",
        action="store",
        help="Where to create the folder")
    PARSER.add_argument(
        "-g",
        "--group",
        default=DEFAULT_GROUP,
        help="The group to assign the folder to. Defaults to {}".format(DEFAULT_GROUP))
    PARSER.add_argument(
        "-p",
        "--perms",
        default=DEFAULT_FOLDER_PERMISSIONS,
        help="The permissions to assign to the folder. Default to {}".format(
            DEFAULT_FOLDER_PERMISSIONS))
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.WARN
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
    logging.getLogger('sh.stream_bufferer').setLevel(logging.WARN)
    logging.getLogger('sh.command.process.streamreader').setLevel(logging.WARN)
    logging.getLogger('sh.command').setLevel(logging.WARN)
    logging.getLogger('sh.streamreader').setLevel(logging.WARN)
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=HANDLERS)
    MANAGER = UserFolderManager(LOG_LEVEL)
    try:
        MANAGER.create_user_folder(ARGS.username, ARGS.folder, ARGS.group, ARGS.perms)
    except Exception as err:
        print(err)
        exit(1)
