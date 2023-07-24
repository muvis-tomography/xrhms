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

    Work out what needs to be uploaded to the public system (currently google drive)

"""
from argparse import ArgumentParser
import sys
import logging
import os
from pathlib import Path
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()

from django.core.exceptions import ObjectDoesNotExist

from django_mysql.locks import Lock
from xrhms.settings import BASE_DIR
from scans.models import ScanAttachment

from drive_uploader import DriveUploader

from xrh_utils import publically_uploadable_video_type
import xrh_utils

LOCK_NAME = "Video Upload"
LOCK_TIMEOUT = 300

DEFAULT_OVERLAY_IMAGE = Path(BASE_DIR, "static", "XRH_Logo_v1_GraphicsOnly.png")

class VideoUploader():
    """
        Manage the task of uploading videos into the google drive
    """

    def __init__(self):
        """
            Basic initialisation
        """
        self._logger = logging.getLogger("Video Uploader")
        self._gdrive = DriveUploader()
        self._gdrive.authenticate() # Set up the drive object

    def find_scan_attachment(self, attachment_id):
        """
            Try to find the required scan attachment by the ID given
            :param int attachment_id: The primary key of the record to find
            :return ScanAttachment: The object required
        """
        try:
            self._logger.debug("Finding attachment ID %s", attachment_id)
            return ScanAttachment.objects.get(pk=attachment_id)
        except ObjectDoesNotExist:
            return None

    def process_all_scan_attachments(self):
        """
            Look for all records that have the to_upload flag set an no URL set
        """
        self._logger.debug("Going to iterate through all scan attachments that need uploading")
        records = ScanAttachment.objects.filter(url__isnull=True, to_upload=True)
        self._logger.info("Records to upload: %d", len(records))
        success = 0
        with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
            for record in records:
                self._logger.debug(record)
                try:
                    if record.url:
                        #User has uploaded it since starting the script
                        #This reduces the possibility of a race condition but it's still there
                        #TODO this needs more thought
                        self._logger.warning("Somebody is messing with the URLs")
                        continue
                    try:
                        if self.upload_scan_attachment(record):
                            success += 1
                    except (ValueError, FileNotFoundError) as err:
                        self._logger.error("Invalid value passed into uploader")
                        self._logger.warning(err)
                        record.to_upload = False # Disable upload flag to stop attempting it again
                        record.save()
                except Exception as exp:
                    self._logger.error(exp)
                    raise
            return (success, len(records))

    def upload_scan_attachment(self, attachment, overlay_image=DEFAULT_OVERLAY_IMAGE):
        """
            Upload the passed in record to YouTube
            :param ScanAttachment attachment: The thing to upload
            :param Path overlay_image: The image to use to apply the watermark
    """
        temp_dir = None # need to be able to keep this in scope for entirity of function
        filename = Path(attachment.attachment.path)
        if not filename.exists():
            self._logger.error("File Not found: %s", str(filename))
            raise FileNotFoundError()
        if not publically_uploadable_video_type(filename):
            raise ValueError("Not a video file")
        if attachment.overlay_position != ScanAttachment.NONE:
            self._logger.debug("Need to apply overlay to video")
            top = True
            left = True
            if(
                    attachment.overlay_position == ScanAttachment.BOTTOM_LEFT or
                    attachment.overlay_position == ScanAttachment.BOTTOM_RIGHT):
                top = False
            if(
                    attachment.overlay_position == ScanAttachment.TOP_RIGHT or
                    attachment.overlay_position == ScanAttachment.BOTTOM_RIGHT):
                left = False
            (temp_dir, output_name) = xrh_utils.apply_overlay(filename, overlay_image, top, left)
            filename = Path(temp_dir.name, output_name)
        title = attachment.name
        self._logger.debug("Using title: %s", title)
        url = self._gdrive.upload(title, filename)
        attachment.url = url
        attachment.save()
        return url

if __name__ == '__main__':
    PARSER = ArgumentParser(
        description="XRHMS video uploader")
    PARSER.add_argument(
        "--version",
        action='version',
        version='%(prog)s 0.1')
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
    ATTACHMENT_TYPE = PARSER.add_mutually_exclusive_group()
    ATTACHMENT_TYPE.add_argument(
        "--scan",
        default=True,
        action="store_true",
        help="Upload the file from the specified scan attachment.")
    ATTACHMENT_ID = PARSER.add_mutually_exclusive_group()
    ATTACHMENT_ID.add_argument(
        "--all",
        action="store_true",
        help="Iterate through all IDs that need uploaded")
    ATTACHMENT_ID.add_argument(
        "--id",
        action="store",
        type=int,
        help="The ID number of the record to upload")
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.WARNING
    if ARGS.quiet:
        LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        LOG_LEVEL = logging.DEBUG
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    CONSOLE_HANDLER = logging.StreamHandler(sys.stderr)
    CONSOLE_HANDLER.setLevel(LOG_LEVEL)
    CONSOLE_HANDLER.setFormatter(FORMATTER)
    HANDLERS = [CONSOLE_HANDLER]
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=HANDLERS)
    logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    logging.getLogger("pyvips.vobject").setLevel(logging.ERROR)
    logging.getLogger("pyvips.voperation").setLevel(logging.ERROR)
    if not ARGS.scan: #Check than an attachment type is specified
        PARSER.error("Must specify a type of record to upload")

    if not (ARGS.id or ARGS.all):
        PARSER.error("Must specify either an ID or all")
    UPLOADER = VideoUploader()
    if ARGS.all:
        if ARGS.scan:
            (SUCCESS, TOTAL) = UPLOADER.process_all_scan_attachments()
            if SUCCESS == TOTAL:
                print("OK: Uploaded {} videos".format(TOTAL))
                sys.exit(0)
            elif TOTAL < 0:
                print("CRITICAL: Unable to run")
                sys.exit(2)
            elif SUCCESS == 0 and TOTAL != 0:
                print("CRITICAL: Unable to upload ANY reports {} attempted".format(TOTAL))
                sys.exit(2)
            elif SUCCESS < TOTAL:
                print("WARNING: Uploaded {}/{} ({})%".format(SUCCESS, TOTAL, int(SUCCESS/TOTAL)))
                sys.exit(1)
        else:
            raise NotImplementedError("Don't know how to upload all entries of that type")
    else:
        if ARGS.scan:
            ATTACHMENT = UPLOADER.find_scan_attachment(ARGS.id)
            if ATTACHMENT:
                UPLOADER.upload_scan_attachment(ATTACHMENT)
            else:
                print("CRITICAL: Unable to find attachment")
                sys.exit(2)
        else:
            raise NotImplementedError("Don't know how to upload that type")
