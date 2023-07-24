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

    Utils to deal with the archiving of data onto external disks

"""
from pathlib import Path
from os.path import ismount
import logging
import subprocess
import sys

from django.core.exceptions import ObjectDoesNotExist

import dataset_processor 

from scans.models import ArchiveDrive, ScanArchive
from xrh_utils import (
    directory_size,
    count_files,
    used_space
)
DEFAULT_PATH = Path("/mnt/archive")
DEFAULT_DEVICE = "sat"
class ArchiveProcessor:
    """
        Utils for dealing with archive disks
    """
    def __init__(
            self,
            path=DEFAULT_PATH,
            log_level=logging.WARNING,
            device=DEFAULT_DEVICE,
            dataset_processor=None):
        """
            Create an object for interacting with an archive drive
            :param Path path: where to find the archive drive
            :param int log_level: default WARNING: how verbose to be
            :param string device: default "sat" The type of device for smartctl to look at
            :param DatasetProcessor dataset_processor: how to handle datasets
        """
        self._logger = logging.getLogger("Archive drive processor")
        self._logger.setLevel(log_level)
        if dataset_processor:
            self._dataset_processor = dataset_processor
        else:
            self._dataset_processor = dataset_processor.DatasetProcessor(log_level)
#        if not ismount(path):
#            raise ValueError("Path must be a mountpoint")
        if not isinstance(path, Path):
            raise ValueError("path must be of type Path")
        self._path = path
        self._logger.debug("Working on path: %s", self._path)
        self._device = device
        self._logger.debug("Using device type: %s", self._device)
        self._smart_data = None

    def create_drive(self):
        """
            Create the DB record for the drive.
            If the drive already exists use that.
            :return ArchiveDrive: The record for the drive
        """
        drive_obj = self.lookup_drive()
        if drive_obj:
            self._logger.info("Drive already registered in DB")
            return drive_obj
        serial_no = self.get_serial_no()
        manufacturer = self.get_manufacturer()
        capacity = self.get_capacity()
        drive_obj = ArchiveDrive(serial_number=serial_no)
        drive_obj.manufacturer = manufacturer
        drive_obj.capacity = capacity
        drive_obj.save()
        return drive_obj

    def lookup_drive(self):
        """
            Lookup the drive in the database using its serial number
            :return Drive: the object for the DB record
        """
        serial_no = self.get_serial_no()
        if not serial_no:
            raise ValueError("Unable to read serial number")
        try:
            drive = ArchiveDrive.objects.get(serial_number=serial_no)
            self._logger.info("Found: %s", drive)
            return drive
        except ObjectDoesNotExist:
            self._logger.debug("No drive found")
            return None

    def drive_in_db(self):
        """
            Check to see if the drive exists in the database
            :return bool: does the DB record exist
        """
        return bool(self.lookup_drive())

    def _get_drive_details(self):
        """
            Read the smartctl data from the HDD and cache it in the object
        """
        self._logger.debug("running smartctl to get details")
        cmd = ["sudo", "smartctl", "--all", "--device={}".format(self._device), self._path]
        output = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            check=True
        )
        self._smart_data = output.stdout.decode("utf-8").split("\n")

    def get_serial_no(self):
        """
            Get the serial number for the drive
            :return string: serial number
        """
        if not self._smart_data:
            self._get_drive_details()
        for line in self._smart_data:
            if line.startswith("Serial Number"):
                serial_no = line.split()[2]
                self._logger.debug("Found serial number: %s", serial_no)
                return serial_no
        return None

    def get_manufacturer(self):
        """
            Get the manufacturer of the drive
            :return string:
        """
        if not self._smart_data:
            self._get_drive_details()
        for line in self._smart_data:
            if line.startswith("Model Family"):
                manufacturer = " ".join(line.split()[2:])
                self._logger.debug("Found manufacturer: %s", manufacturer)
                return manufacturer
        return None

    def get_capacity(self):
        """
            Get the capacity of the drive in GB
            :return float capacity
        """
        if not self._smart_data:
            self._get_drive_details()
        for line in self._smart_data:
            if line.startswith("User Capacity"):
                capacity_bytes = float(line.split()[2].replace(",", ""))
                capacity_gb = capacity_bytes / 1024**3
                self._logger.debug("Found capacity: %f", capacity_gb)
                return capacity_gb
        return None

    def update_drive(self):
        """
            Update the db details about the drive:
            updates the following:
            * list of datasets on the drive
            * estimated usage
            * number of files
            Warning this may be slow
            : return bool: whether or not datasets were scanned ok
        """

        drive = self.lookup_drive()
        drive.estimated_usage = used_space(self._path)
        drive.no_files = count_files(self._path)
        return self.index_datasets()

    def index_datasets(self):
        """
            Scan the drive and make sure that records exist for all scans on it
            :return bool, did this complete ok
        """
        success = True
        drive = self.lookup_drive()
        datasets = self._dataset_processor.list_datasets(self._path)
        self._logger.debug("Found %d datasets", len(datasets))
        pre_existing = 0
        for dataset in datasets:
            try:
                scan_obj = self._dataset_processor.lookup_scan(dataset_path)
            except ObjectDoesNotExist:
                self._logger.error("Unable to find DB record for scan")
                success = False
            try:
                dataset_path = Path(dataset)
                archive = ScanArchive.objects.get(
                    scan=scan_obj,
                    drive=drive,
                    path=dataset_path)
                # If we complete the above then the record exists
                pre_existing += 1
                continue
            except ObjectDoesNotExist:
                #record doesn't exist so create it
                archive = ScanArchive()
                archive.drive = drive
                archive.path = dataset.parent
                archive.scan = scan_obj
                archive.total_size = float(directory_size(dataset_path)) / 1024**3
                archive.file_count = count_files(dataset_path)
                archive.save()
        self._logger.info(
            "%d/%d (%.1f) records already existed",
            pre_existing, len(datasets), float(pre_existing) / len(datasets))
        return success
