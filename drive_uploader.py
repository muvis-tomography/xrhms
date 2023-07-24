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

    Class to upload files into google drive for sharing
"""

import logging
from argparse import ArgumentParser
from sys import exit, stderr
from pathlib import Path
from googleapiclient.errors import HttpError
from pydrive2.drive import GoogleDrive
from pydrive2.auth import GoogleAuth

from xrh_utils import publically_uploadable_video_type
UPLOAD_FOLDER = "xrhms-uploads" # Folder to store into in gdrive

class DriveUploader():
    """
        A class which can be used to upload files into google drive
    """

    def __init__(self):
        """
            Initialise the objects
        """
        self._logger = logging.getLogger("Google Drive Uploader")
        self._gauth = None
        self._gdrive = None
        self._folder_id = None

    def authenticate(self, ui=False): #pylint: disable=invalid-name
        """
            Based on code from
            https://www.programcreek.com/python/example/88814/pydrive.drive.GoogleDrive
            :param boolean ui: Default False. Is a UI available to run the authentication
        """
        gauth = GoogleAuth()
        try:
            #Use the settings.yaml file for configuration to get the required paths
            gauth.LoadCredentialsFile()
            if gauth.credentials is None:
                #No credentials available
                self._logger.warning("No credentials")
                if ui:
                    #Running with UI
                    self._logger.debug("Need to use CLI to authenticate")
                    gauth.CommandLineAuth()
                else:
                    #We're dooomed
                    self._logger.critical("Please use commandline tool to authenticate")
                    raise ValueError("Interactive authentication needed")
            if gauth.access_token_expired:
                self._logger.debug("Refreshing existing token")
                gauth.Refresh()
            else:
                self._logger.debug("Credentials in date - authorising")
                gauth.Authorize()
            gauth.SaveCredentialsFile()
            self._logger.debug("Successfully authenticated")
            self._gauth = gauth
            self._gdrive = GoogleDrive(gauth)
        except:
            self._logger.critical("Unable to authenticate, CANNOT continue")
            raise ValueError("Unable to authenicate") #pylint: disable=raise-missing-from

    def upload(self, title, filepath, folder_name=UPLOAD_FOLDER):
        """
            Upload the specified file to google drive
            :param string title: The title to give the file when uploaded
            :param Path filepath: The file to upload
            :param string folder_name: The name of the gdrive folder to upload to
            :return string: The public URL of the uploaded file
        """
        if not filepath.exists():
            self._logger.error("Cannot find file %s", filepath)
            raise FileNotFoundError("Cannot find file {}".format(str(filepath)))
        if not title:
            self._logger.error("Must specify a title")
            raise ValueError("Must specify a title")
        if not self._gdrive:
            self._logger.error("Must authenticate before uploading")
            raise ValueError("Not authenticated")
        if not self._folder_id:
            self._logger.info("Not got the folder ID")
            self._get_folder_id(folder_name)
        self._logger.debug("Using folder ID %s", self._folder_id)
        gfile = self._gdrive.CreateFile({'parents' : [{'id': self._folder_id}]})
        gfile.SetContentFile(str(filepath))
        gfile["title"] = title
        gfile.Upload()
        gfile.InsertPermission({"type" :"anyone", "role": "reader", "withLink":True})
        self._logger.debug("Original URL: %s", gfile["alternateLink"])
        url = gfile["alternateLink"].split("?")[0] # remove the GET params off the end to tidy it
        self._logger.info("Cleaned URL: %s", url)
        return url

    def _get_folder_id(self, folder_name=UPLOAD_FOLDER):
        """
            Get the ID for the folder to upload to
            :param string folder_name: The GDrive folder to upload to
        """
        try:
            self._logger.debug("Getting ID for folder: %s", folder_name)
            folders = self._gdrive.ListFile(
                {"q" :"title='{}'and mimeType='application/vnd.google-apps.folder' and trashed=false".format( #pylint:disable=line-too-long
                    folder_name)}).GetList()
            if len(folders) != 1:
                self._logger.error("Found %d folders, not sure how to procced", len(folders))
                raise ValueError("Incorrect number of folders found")
            self._folder_id = folders[0]["id"]
            return self._folder_id
        except HttpError:
            self._logger.error("Unable to get folder ID")
            raise

    def get_quota(self):
        """
            Check how much quota is available in the google driver account
            :return (available, total, percentage)
        """
        if not self._gdrive:
            self._logger.error("Must authenticate first")
            raise ValueError("Must authenticate first")
        about = self._gdrive.GetAbout()
        total = int(about["quotaBytesTotal"])
        used = int(about["quotaBytesUsedAggregate"])
        percentage = used / total * 100
        self._logger.info("Used: %d, Total: %d, Used %d%%", used, total, int(percentage))
        return (used, total, percentage)

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Google drive upload")
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
        "-a",
        "--authenticate",
        action="store_true",
        help="Only perform the authentication, don't upload anything")
    PARSER.add_argument(
        "file",
        nargs='?',
        action="store",
        type=str,
        help="The file to upload")
    PARSER.add_argument(
        "--version",
        action='version',
        version='%(prog)s 0.2')
    PARSER.add_argument(
        "--quota",
        action="store_true",
        help="Check the amount of space remaining")
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
    logging.getLogger("googleapiclient.discovery").setLevel(logging.WARN)
    LOGGER = logging.getLogger("Drive Upload CMD Line")
    UPLOADER = DriveUploader()
    UPLOADER.authenticate(True)
    if ARGS.authenticate:
        print("Authenticate succeeded")
        exit(0)
    if ARGS.quota:
        (USED, TOTAL, PERCENTAGE) = UPLOADER.get_quota()
        print("{},{},{:.1f}".format(USED, TOTAL, PERCENTAGE))
        exit(0)
    FILE = Path(ARGS.file)
    if not FILE.exists():
        LOGGER.critical("File not found: %s", FILE)
        exit(1)
    if not publically_uploadable_video_type(FILE):
        LOGGER.critical("File type not in list of allowable uploads")
        exit(2)
    TITLE = FILE.stem
    print(URL=UPLOADER.upload(TITLE, FILE))
