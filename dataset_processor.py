#pylint: disable=too-many-lines
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
    
    Handle all the processing and moving of scan datasets

"""
import logging
from pathlib import Path
import os
from os import makedirs
from datetime import datetime
import shutil
import subprocess

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xrhms.settings")
django.setup()
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils import timezone
from django_mysql.exceptions import TimeoutError #pylint: disable=redefined-builtin
from django_mysql.locks import Lock
from xrhms_exceptions import XrhmsIgnore
from xtek_parser import XtekParser
from vsi_parser import VsiParser

from muvis.models import MuvisBug
from samples.models import Sample, SampleType
from samples.models.xrh_id import (
    check_digit_ok as xrh_id_validate,
    XrhIdValidationError,
    get_numeric as xrh_id_get_numeric,
    get_suffix as xrh_id_get_suffix,
)
from scans.models.dataset_status import(
    DATASET_ARCHIVED_DISK,
    DATASET_MOVING,
    DATASET_ONLINE,
)
from scans.models import (
    Machine,
    Share,
    ScheduledMove,
    SidecarStatus,
    generate_sidecar_filename,
    load_sidecar,
    Scan,
    UserCopy,
)
from xrh_utils import (
    calculate_file_hash,
    convert_filesize,
    count_eaDir,
    delete_eaDir,
    directory_size,
    free_space,
    mount_free_percent,
)
from archive_processor import ArchiveProcessor

LOCK_TIMEOUT = 300 #Wait for this many secodns before giving up on getting the lock
LOCK_NAME = "xtek_lock"


class DatasetProcessor():
    """
        Class to handle the processing of datasets and their moves
    """

    def __init__(self, log_level=logging.WARNING):
        """
            Standard constructor.
            Loads the modular parsers in for different datasets
            :param int log_level: How verbose to be
        """
        self._logger = logging.getLogger("Dataset processor")
        self._log_level = log_level
        self._logger.setLevel(log_level)
        self._parsers = [
            XtekParser(log_level),
            VsiParser(log_level)
        ]
        self._build_parser_lookup()
        self._logger.info("Initialised with %d parsers", len(self._parsers))

    def _build_parser_lookup(self):
        """
            Build a dictionary containing a mapping from filename extension to parser
        """
        self._parser_dict = {}
        for parser in self._parsers:
            for ext in parser.extensions():
                self._parser_dict[ext.strip(".")] = parser
        self._logger.debug("Parser dictionary: %r", self._parser_dict)

    def _lookup_parser(self, extension):
        """
            Lookup the extension to work out which parser to use
        """
        return self._parser_dict[extension.strip(".")]

    def process_directory(self, directory):
        """
            Uses each parser to look in the specified directory to see if there are any changes
            Must acquire lock
            :param Path directory: The directory to be scanned
        """
        if not directory.exists():
            raise ValueError("{} must exist".format(directory))
        try:
            with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
                process_ok = True
                for parser in self._parsers:
                    self._logger.debug("Using parser %s", parser)
                    files = parser.list_files(directory)
                    self._logger.debug("Found %d files", len(files))
                    for fname in files:
                        try:
                            self._logger.debug("Processing: %s", fname)
                            sidecar_filename = generate_sidecar_filename(fname)
                            self._logger.debug("sidecar filename: %s", sidecar_filename)
                            path = self._extract_path(fname)
                            share = self._extract_share(fname)
                            db_entry = None
                            if sidecar_filename.exists():
                                try:
                                    db_entry_s = load_sidecar(sidecar_filename)
                                    sidecar_status = db_entry_s.check_sidecar_status(fname)
                                    self._logger.debug("Sidecar status: %s", sidecar_status.name)
                                    if sidecar_status == SidecarStatus.COPIED:
                                        self._logger.debug("copy found adding to DB")
                                        db_entry = parser.process_file(fname)
                                        # ^^  This will fix the wrong sidecar
                                    elif sidecar_status == SidecarStatus.MOVED:
                                        self._logger.debug("dataset moved")
                                        db_entry_s.share = share
                                        db_entry_s.path = path
                                        db_entry_s.save()
                                        db_entry = db_entry_s # Use the found record
                                    elif sidecar_status == SidecarStatus.OK:
                                        db_entry = db_entry_s
                                    elif sidecar_status == SidecarStatus.INVALID:
                                        raise ValueError("How can a sidecar not refer to itself?")
                                except (ObjectDoesNotExist, KeyError):
                                    pass
                                except subprocess.CalledProcessError:
                                    self._logger.error("Failed to run a required subprocess")
                                    process_ok = False
                            else:
                                self._logger.debug("Sidecar not found")
                            if not db_entry: #haven't got the db entry - have to search differently
                                #This could be because it's new, or because the sidecar didn't exist
                                short_fname = fname.name
                                if Scan.objects.filter(
                                        share=share,
                                        path=path,
                                        filename=short_fname):
                                    #Found a record of the file - therefore it didn't have a sidecar
                                    db_entry = Scan.objects.get(
                                        share=share,
                                        path=path,
                                        filename=short_fname)
                                    self._logger.debug(
                                        "Found existing record pk=%d",
                                        db_entry.pk)
                                    self._logger.warning(
                                        "Record %d didn't have a sidecar. Recreating...",
                                        db_entry.pk)
                                    db_entry.save_sidecar()
                            calculated_checksum = calculate_file_hash(fname)
                            self._logger.debug("Calculated checksum: %s", calculated_checksum)
                            if db_entry:
                                if db_entry.checksum == calculated_checksum:
                                    self._logger.debug(
                                        "Checksums match, therefore it hasn't changed")
                                else:
                                    self._logger.debug("Checksum DO NOT match, it has changed")
                                    parser.process_file(fname, db_entry)
                            else:
                                self._logger.debug("No entry in database found")
                                self._logger.debug("Creating entry")
                                db_entry = parser.get_model()()
                                db_entry.projection0deg = None
                                db_entry.projection90deg = None
                                db_entry = self._parse_filepath(fname, db_entry)
                                db_entry = parser.process_file(fname, db_entry)
                                db_entry.find_parent()
                                db_entry.generate_sample_info()
                            parser.process_associated_files(db_entry)
                        except XrhmsIgnore:
                            self._logger.info("Ignoring file (%s) due to option", fname)
                        except Exception as exp: #pylint: disable=broad-except
                            self._logger.error("Failed to process %s", fname)
                            self._logger.error(exp)
                            process_ok = False
                if not process_ok:
                    self._logger.error("Something went wrong processing files")
                return process_ok
        except TimeoutError:
            self._logger.critical("Unable to get DB lock")
            return False


    def process_move_queue(self, count=None):
        """
            Process the queue of scan datasets to be moved
        """
        queue = ScheduledMove.objects.filter(date_executed__isnull=True)
        self._logger.info("Items in queue: %d", len(queue))
        if count:
            self._logger.info("Only scheduled to move %d/%d", count, len(queue))
        else:
            count = len(queue)
        processed = 0
        archived_datasets_to_disk = False
        # have any datasets been archived to disk requiring re scanning, but default to not
        for move in queue:
            if processed == count: # do this at the start as there are multiple places it can loop
                break
            processed += 1
            self._logger.info("Processing %d/%d", processed, count)
            dst_share = move.destination
            group_by_sample = move.group_by_sample
            scan = move.scan
            self._logger.info("Scan being processed %s", scan)
            self._logger.debug("Current location %s", scan.full_path())
            self._logger.info("Destination share %s", dst_share)
            if scan.dataset_status != DATASET_ONLINE:
                self._logger.error("Dataset not online unable to move")
                move.success = False
                move.output = "Dataset status: {} unable to move".format(scan.dataset_status)
                move.date_executed = timezone.now()
                move.save()
                continue
            output = []
            if dst_share.default_status == DATASET_ARCHIVED_DISK:
                archived_datasets_to_disk = True
                self._logger.debug("Sent some files to disk - need to index drive")
                archive_processor = ArchiveProcessor(
                    log_level=self._log_level,
                    dataset_processor=self)
                archive_drive = archive_processor.lookup_drive()
                if not archive_drive:
                    move.success = False
                    self._logger.error(
                        "Failed to find disk in DB, check it's inserted and initialised")
                    move.output = "Failed to find archive drive"
                    move.save()
                    continue
            if scan.share == dst_share:
                self._logger.error("Cannot move scan on same share")
                output.append("Cannot move scan on same share")
                move.success = True # It's in its correct position so I guess this is a  success
                move.save()
            else:
                try:
                    src = Path(scan.share.linux_mnt_point, scan.path)
                    self._logger.debug("Moving from %s", src)
                    path_arr = Path(scan.path).parts
                    self._logger.debug("Path arr: %r", path_arr)
                    #Use as default path can be overided
                    if len(path_arr) > 1:
                        dst = Path(dst_share.linux_mnt_point, path_arr[0])
                    else:
                        dst = Path(dst_share.linux_mnt_point)
                    pre_grouped = False
                    if len(path_arr) > 2:
                        try:
                            pre_grouped = xrh_id_validate(path_arr[1])
                            self._logger.debug("Already in sample folder")
                            output.append("Already in sample folder")
                        except XrhIdValidationError:
                            pass
                    if (
                            (pre_grouped and len(path_arr) >= 4) or
                            (not pre_grouped and len(path_arr) >= 3)):
                        self._logger.warning("This is a sub dataset please move the top level")
                        output.append("This is a sub dataset please move the top level")
                        move.success = False
                    else:
                        if group_by_sample:
                            self._logger.debug("Need to move into sample folder")
                            if scan.sample:
                                dst = Path(
                                    dst_share.linux_mnt_point,
                                    path_arr[0],
                                    scan.sample.xrh_id())
                            else:
                                self._logger.error(
                                    "No sample ID set cannot move into sample folder")
                                output.append("No Sample ID set cannot move into sample folder")
                        self._logger.debug("Moving to %s", dst)
                        if not dst.exists():
                            makedirs(dst)
                            self._logger.debug("Created directory")
                        eaDir_count = count_eaDir(src) #pylint: disable=invalid-name
                        if eaDir_count:
                            self._logger.warning("Found %s eadirectories in subtree", eaDir_count)
                            delete_eaDir(src)
                            eaDir_count = count_eaDir(src) #pylint: disable=invalid-name
                            if eaDir_count:  #pylint: disable=no-else-return
                                self._logger.error("Unable to delete eaDirs. Still (%d) remaining", eaDir_count)
                                output.append("Unable to delete eaDir")
                                move.date_executed = timezone.now()
                                move.success = False
                                move.save()
                                return
                            else:
                                self._logger.debug("eaDir removed successfully")
                        else:
                            self._logger.debug("No eaDir folders found")
                        move.success = self.move_subtree(src, dst)
                except Exception as exp: #pylint: disable=broad-except
                    self._logger.error(exp)
                    move.success = False
                    output.append(str(exp))
            if archived_datasets_to_disk:
                archive_processor.index_datasets()
            if output:
                move.output = "\n".join(output)
            move.date_executed = timezone.now()
            move.save()


    def move_subtree(self, src, dst, generate_extra=False):
        """
            Move all files on the src path to the destination.
            Will update all the records to known datasets
            :param Path src: The source sub tree
            :param Path dst: Where to move to
            :param Boolean generate extra folder - should the extra folder be generated?
            :return Boolean: Success
        """
        if self.count_moving() > 0:
            self._logger.critical("Move already in progress")
            raise ValueError("Moving > 0")
        #Check the source exists
        if src.name == "CTData":
            self._logger.error(
                "This will create nested CTData folders.  Use CTData/* to move everything")
            raise ValueError("Don't want to create nested CTData folders")
        if not src.exists():
            self._logger.error("The source directory (%s) must exist.", src)
            raise FileNotFoundError("The source directory must exist.")
        #Check the destionation exists
        if not dst.exists():
            self._logger.error("The destination (%s) must exist.", dst)
            raise FileNotFoundError("The destination must exist")
        if not dst.is_dir():
            self._logger.error("The destination (%s) must be a directory", dst)
            raise NotADirectoryError("The destination must be a directory")
        #Check that source is a location that is known about
        try:
            src_share = self._extract_share(src, True)
        except ValueError:
            self._logger.error("No record of source location (%s) in DB", src)
            raise ValueError("No record of source location in DB") from None
        #Check that the destionation is a location is known about
        try:
            dst_share = self._extract_share(dst, True)
        except ValueError:
            self._logger.error("No record of Destionation location (%s) in DB", dst)
            raise ValueError("No record of destination location in DB") from None

        #Calculate the size of the move
        src_size = directory_size(src)
        self._logger.info("Data to move: %s", convert_filesize(src_size))
        #If dst is a different share check it has enough space
        if src_share != dst_share:
            self._logger.debug("Moving data between shares")
            dst_space = free_space(dst)
            self._logger.info("Free space on destination share %s", convert_filesize(
                dst_space))
            if dst_space <= src_size:
                self._logger.error("Not enough space on destination")
                raise ValueError("Not enough space on destination")
        #Check all xtek files are in the database
        ##xtekctfiles
        self._logger.info("Acquiring lock")
        try:
            with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
                self._logger.info("Lock acquired")
                datasets = []
                for parser in self._parsers:
                    datasets += parser.list_files(src)
                self._logger.info(
                    "Found %d dataset files in structure to be moved", len(datasets))
                not_found_count = 0
                for xfile in datasets:
                    self._logger.debug("Extracting share & path from %s", xfile)
                    xshare = self._extract_share(xfile)
                    xpath = self._extract_path(xfile)
                    self._logger.debug("Expect it to be on share: %r (%d)", xshare, xshare.pk)
                    self._logger.debug("Expect it to be on path: %s", xpath)
                    if not Scan.objects.filter(
                            share=xshare, path=xpath, filename=xfile.name).exists():
                        self._logger.warning("File not found in DB adding: %s", xfile)
                        fname_extension = xfile.suffix
                        for parser in self._parsers:
                            if fname_extension in parser.extensions():
                                parser.process_file(xfile)
                        not_found_count += 1
                    entry = Scan.objects.get(share=xshare, path=xpath, filename=xfile.name)
                    entry.dataset_status = DATASET_MOVING
                    entry.dataset_status_last_updated = timezone.now()
                    entry.save()
                if not_found_count:
                    self._logger.warning("Added %d files into database", not_found_count)
                self._logger.debug("Moving all files")
                self._logger.debug("SRC: %s, DST: %s", src, dst)
                shutil.move(str(src), str(dst))
                if datasets:
                    self._logger.debug("Updating database records")
                    for xfile in datasets:
                        self._logger.debug("Updating %s", xfile)
                        xshare = self._extract_share(xfile)
                        self._logger.debug("share = %s", xshare)
                        xpath = self._extract_path(xfile)
                        self._logger.debug("path = %s", xpath)
                        entry = Scan.objects.get(
                            share=xshare, path=xpath, filename=xfile.name)
                        src_location = xfile.parent
                        self._logger.debug("Source location: %s", src_location)
                        src_rel_location = src_location.relative_to(src.parent)
                        self._logger.debug("Source relative location: %s", src_rel_location)
                        dst_location = dst.joinpath(src_rel_location)
                        self._logger.debug("Destination location: %s", dst_location)
                        dst_path = self._extract_path(dst_location, True)
                        self._logger.debug("Destination path: %s", dst_path)
                        dst_share = self._extract_share(dst_location, True)
                        self._logger.debug("Destination share: %s", dst_share)
                        entry.path = dst_path
                        entry.share = dst_share
                        entry.dataset_status = dst_share.default_status
                        entry.dataset_status_last_updated = timezone.now()
                        entry.save()
                        if dst_share.generate_extra_folder or generate_extra:
                            self._logger.debug("Need to generate extra folder")
                            extra_path = Path(dst_location, entry.full_path().stem)
                            if extra_path.exists():
                                self.generate_extra(entry, extra_path)
                            else:
                                ##If folder doesn't exist then don't try to create the extra folder
                                # This could be because:
                                    # auto reconstruction wasn't enabled
                                    # the autoreconstruction was deleted
                                self._logger.warning(
                                    "Extra path doesn't exist likely it wasn't auto reconstructed")
                self._logger.debug("Moving complete")
            return True
        except TimeoutError:
            self._logger.critical("Unable to get DB lock")
            return False

    def _extract_share(self, fname, is_dir=False):
        """
            Work out which share the fname is on
            :param Path fname: Path to examine
            :param boolean is_dir: Is a directory being passed in rather than a file
        """
        if is_dir:
            dname = fname
        else:
            dname = fname.parent
        self._logger.debug("Directory name: %s", dname)
        path_arr = dname.parts
        if len(path_arr) < 3:
            self._logger.error("Unable to extract mount point from %s", dname)
            raise ValueError("Invalid directory name ({})".format(dname))
        mnt_point = path_arr[2]
        self._logger.debug("Dataset on mountpoint: %s", mnt_point)
        try:
            share = Share.objects.get(linux_mnt_point__contains=mnt_point)
            return share
        except ObjectDoesNotExist:
            self._logger.error("Unable to match mount_point (%s) to value in DB", mnt_point)
            raise ValueError("Unable to match mount_point ({}) to value in DB".format(mnt_point))  #pylint: disable=raise-missing-from

    def _extract_path(self, fname, is_dir=False):
        """
            Work out the path to the file on the share
            :param Path fname: Path to examine
            :param boolean is_dir: Is a directory being passed in rather than a file
        """
        if is_dir:
            path_arr = fname.parts
        else:
            path_arr = fname.parent.parts
        if len(path_arr) < 4:
            #It's on the root of the share
            self._logger.debug("Path doesn't have a directory component")
            return ""
        return "/".join(path_arr[3:])


    def _parse_scan_name(self, scan_name):
        """
            Exctract the required information from the dataset name
            :param string scan_name: The path to extract information from
        """
        #date_scanner_bug_operator_sample_other
        data = {}
        arr = scan_name.strip("\\").split("_")
        self._logger.debug("Parsing scan name %s", scan_name)
        arg_count = len(arr)
        self._logger.debug("Found %d arguments", arg_count)
        if arg_count < 5:
            self._logger.debug(arr)
            self._logger.error("Not enough elements (%d) in dataset name to be parsed", len(arr))
            raise ValueError("Not enough elements in dataset name to be parsed")
        data["date"] = datetime.strptime(arr[0], "%Y%m%d").date()
        self._logger.debug("Scan date: %r", data["date"])
        data["scanner"] = arr[1]
        self._logger.debug("Scanner: %s", data["scanner"])
        try:
            data["bug_id"] = int(arr[2])
            self._logger.debug("Muvis bug ID: %d", data["bug_id"])
        except ValueError:
            self._logger.warning("Invalid bug ID (%s) found", arr[2])
            data["bug_id"] = None
        data["operator"] = arr[3]
        self._logger.debug("Operator: %s", data["operator"])
        data["other"] = None
        try:
            if xrh_id_validate(arr[4]):
                #There is a valid sample ID set in the filename
                data["sample_id"] = arr[4]
                self._logger.debug("Sample ID: %s", data["sample_id"])
                if arg_count >= 6:
                    data["other"] = "_".join(arr[5:])
            else:
                data["other"] = "_".join(arr[4:])
                data["sample_id"] = None
        except XrhIdValidationError:
            data["other"] = "_".join(arr[4:])
            data["sample_id"] = None
        self._logger.debug("Other information: %s", data["other"])
        return data

    def count_moving(self):
        """
            Count the number of files marked as moving
            :return int: The number of files marked as moving
        """
        count = Scan.objects.filter(dataset_status=DATASET_MOVING).count()
        self._logger.debug("Moving count: %d", count)
        return count

    def check_all_exist(self):
        """
            Go through all records in the db and check they are still on the
            filesystem where they are expected to be.
            :return int: The number of records where filesystem & db don't match
        """
        self._logger.debug("Check all records in database exist in filesystem")
        self._logger.info("Acquiring lock")
        try:
            with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
                self._logger.info("Got lock")
                if self.count_moving() > 0:
                    self._logger.critical("Moving operation in progress")
                    return -1
                all_records = Scan.objects.all()
                self._logger.info("%d records to process", len(all_records))
                count = 0
                change_count = 0
                for record in all_records:
                    if not self.check_exists(record):
                        self._logger.debug("DIFFERENT: %s", record)
                        change_count += 1
                    count += 1
                    if count > 0 and (count % 20) == 0:
                        self._logger.info("Processed %d records", count)
                self._logger.info("Processed all records (%d)", count)
                return change_count
        except TimeoutError:
            self._logger.critical("Unable to get DB lock")
            return -2

    def check_exists(self, entry): #pylint: disable=no-self-use
        """
            Check the dataset file specified in the entry exists
            Returns true if the filesystem and DB match
        """
        return not entry.update_exists()[1]

    def _parse_scan_name(self, scan_name):
        """
            Exctract the required information from the dataset name
        """
        #date_scanner_bug_operator_sample_other
        data = {}
        arr = scan_name.strip("\\").split("_")
        self._logger.debug("Parsing scan name %s", scan_name)
        arg_count = len(arr)
        self._logger.debug("Found %d arguments", arg_count)
        if arg_count < 5:
            self._logger.debug(arr)
            self._logger.error("Not enough elements (%d) in dataset name to be parsed", len(arr))
            raise ValueError("Not enough elements in dataset name to be parsed")
        data["date"] = datetime.strptime(arr[0], "%Y%m%d").date()
        self._logger.debug("Scan date: %r", data["date"])
        data["scanner"] = arr[1]
        self._logger.debug("Scanner: %s", data["scanner"])
        try:
            data["bug_id"] = int(arr[2])
            self._logger.debug("Muvis bug ID: %d", data["bug_id"])
        except ValueError:
            self._logger.warning("Invalid bug ID (%s) found", arr[2])
            data["bug_id"] = None
        data["operator"] = arr[3]
        self._logger.debug("Operator: %s", data["operator"])
        data["other"] = None
        try:
            if xrh_id_validate(arr[4]):
                #There is a valid sample ID set in the filename
                data["sample_id"] = arr[4]
                self._logger.debug("Sample ID: %s", data["sample_id"])
                if arg_count >= 6:
                    data["other"] = "_".join(arr[5:])
            else:
                data["other"] = "_".join(arr[4:])
                data["sample_id"] = None
        except XrhIdValidationError:
            data["other"] = "_".join(arr[4:])
            data["sample_id"] = None
        self._logger.debug("Other information: %s", data["other"])
        return data

    def _parse_filepath(self, fpath, scan_data):
        """
            Parse out the details from the path to the dataset

            :param scan_data: The Django object in which to store the data found
        """
        self._logger.debug("Extracting data from path")
        if not scan_data:
            self._logger.error("Must pass in a scan data object to populate")
            raise ValueError("Must have a scan data object to populate data into")
        path = Path(fpath)
        path_arr = path.parts
        dataset = path.parent
        if len(path_arr) < 3:
            #Expect atleast /mnt/share/dataset
            #Anything else will not contain enough information
            self._logger.debug(path_arr)
            self._logger.error("Dataset path (%s) doesn't contain enough elements", dataset)
            raise ValueError("Dataset path ({}) doesn't contain enough elements".format(dataset))
        meta_data = self._parse_scan_name(path.stem)
        mnt_point = path_arr[2]
        self._logger.debug("Dataset on mountpoint: %s", mnt_point)
        try:
            share = Share.objects.get(linux_mnt_point__contains=mnt_point)
        except ObjectDoesNotExist:
            self._logger.error("Unable to match mount_point (%s) to value in DB", mnt_point)
            raise ValueError("Unable to match mount_point ({}) to value in DB".format(mnt_point))  #pylint: disable=raise-missing-from
        try:
            scanner = Machine.objects.get(name__icontains=meta_data["scanner"])
        except ObjectDoesNotExist:
            self._logger.error(
                "Unable to match scanner (%s) to known machine", meta_data["scanner"])
            raise ValueError( #pylint: disable=raise-missing-from
                "Unable to match scanner ({}) to known machine".format(meta_data["scanner"]))
        if meta_data["sample_id"]:
            xrh_id_number = xrh_id_get_numeric(
                meta_data["sample_id"], False) #don't want the check digit
            xrh_id_suffix = xrh_id_get_suffix(meta_data["sample_id"])
            self._logger.debug("Looking for suffix: %s", xrh_id_suffix)
            try:
                sample = Sample.objects.get(
                    xrh_id_number=xrh_id_number,
                    xrh_id_suffix=xrh_id_suffix)
            except ObjectDoesNotExist:
                self._logger.info("Attempt 1 to find sample failed")
                try:
                    #suffix was probably null in DB as it's using the suffix from the type
                    sample_type = SampleType.objects.get(suffix=xrh_id_suffix)
                    self._logger.debug("Looking for sample type %s", sample_type)
                    sample = Sample.objects.get(
                        xrh_id_number=xrh_id_number,
                        sample_type=sample_type,
                        xrh_id_suffix=None) # exclude other blocks
                except ObjectDoesNotExist:
                    self._logger.error(
                        "Unable to match sample ID %s to a record", meta_data["sample_id"])
                    sample = None
        else:
            sample = None
        if meta_data["bug_id"]:
            try:
                muvis_id = MuvisBug.objects.get(pk=meta_data["bug_id"])
            except ObjectDoesNotExist:
                self._logger.error(
                    "Unable to match Bug ID (%s) to known bug", meta_data["bug_id"])
                muvis_id = None
        else:
            muvis_id = None
        scan_data.scan_date = meta_data["date"]
        scan_data.scanner = scanner
        scan_data.operator = meta_data["operator"]
        scan_data.sample = sample
        scan_data.share = share
        scan_data.path = self._extract_path(fpath)
        scan_data.filename = path.name
        scan_data.muvis_bug = muvis_id
        return scan_data

    def generate_extra(self, scan, dst_folder):
        """
            Generate the extra folder containing all other data about the scan set
            :param Scan scan: The scan to generate the extra folder
            :param Path dst_folder: where to put the extra folder
            :return int: the number of files copied
        """
        files_copied = 0
        #input validation
        self._logger.debug("Destination folder: %s", dst_folder)
        if not isinstance(dst_folder, Path):
            raise ValueError("dst folder must be a path")
        if not dst_folder.exists():
            raise ValueError("dst folder must exist")
        #create extra folder if needed
        extra_folder = Path(dst_folder, "extra")
        if not extra_folder.exists():
            self._logger.debug("Creating extra folder")
            extra_folder.mkdir()
        #sample photos
        sample = scan.sample
        if sample:
            sample_attachments = sample.sampleattachment_set.all()
            self._logger.debug("Copying %d sample attachments", len(sample_attachments))
            for attachment in sample_attachments:
                shutil.copy(attachment.attachment.path, extra_folder)
            files_copied += len(sample_attachments)
        #reports
        reports = scan.reportscanmapping_set.filter(report__generation_success=True)
        self._logger.debug("Copying %d reports", len(reports))
        for report in reports:
            shutil.copy(report.report.report.path, extra_folder)
        files_copied += len(reports)
        #projections / xy slice
        if scan.projection0deg.name is not None and scan.projection0deg.name != '':
            shutil.copy(scan.projection0deg.path, extra_folder)
            files_copied += 1
        if  scan.projection90deg.name is not None and scan.projection90deg.name != '':
            shutil.copy(scan.projection90deg.path, extra_folder)
            files_copied += 1
        if  scan.xyslice.name is not None and scan.xyslice.name != '':
            shutil.copy(scan.xyslice.path, extra_folder)
            files_copied += 1
        #scan attachments
        scan_attachments = scan.scanattachment_set.filter(
            attachment_type__include_in_extra_folder=True)
        self._logger.debug("Copying %d scan attachments", len(scan_attachments))
        for attachment in scan_attachments:
            shutil.copy(attachment.attachment.path, extra_folder)
        files_copied += len(scan_attachments)
        self._logger.debug("Copied %d files into extra folder", files_copied)
        return files_copied

    def list_datasets(self, path):
        """
            List all the datasets on the path specified
            :param Path path: the path to look at
            :return List: datasets
        """
        if not isinstance(path, Path):
            raise ValueError("Must pass in a Path")
        if not path.exists():
            raise ValueError("Path must exist")
        datasets = []
        for parser in self._parsers:
            datasets += parser.list_files(path)
        self._logger.debug("Found %d datasets", len(datasets))
        return datasets

    def lookup_dataset(self, fname):
        """
            Lookup the dataset object based on the path of the dataset
            :param Path fname: the location of disk of the dataset
            :return Scan: the found scan or none if not found
        """
        if not isinstance(fname, Path):
            raise ValueError("path must be a Path object")
        if not fname.exists():
            raise ValueError("Path does not exist")
        try:
            self._logger.debug("Looking for DB record for %s:", fname)
            sidecar_filename = generate_sidecar_filename(fname)
            self._logger.debug("Sidecar should be: %s", sidecar_filename)
            if sidecar_filename.exists():
                scan = load_sidecar(sidecar_filename)
                self._logger.debug("Found %s using sidecar file")
                return scan
            #unable to locate sidecar file, trying the old fashioned way
            path = self._extract_path(fname)
            share = self._extract_share(fname)
            short_fname = fname.name
            scan = Scan.objects.get(
                share=share,
                path=path,
                filename=short_fname)
            self._logger.debug("Found %s using path / filename")
            scan.save_sidecar()
            self._logger.debug("Recreated sidecar file")
            return scan
        except ObjectDoesNotExist:
            self._logger.warning("Unable for find scan from path %s in DB", path)
            return None


    def cleanup_user_space(self):
        """
            Look at all the datasets in the user folder & delete the ones eligible for deletion.
            Uses the expiration interval set in the database.
            :return (int, int): (Number deleted, Total)
        """
        datasets = UserCopy.objects.filter(
            copy_success=True, # have been copied to folder
            deletion_success__isnull=True # haven't attempted to delete
        )
        self._logger.info("Currently storing %d user datasets", datasets.count())
        eligible = []
        folder_size = 0
        for dataset in datasets:
            if dataset.deletion_eligible():
                eligible.append(dataset)
                folder_size += dataset.size_on_disk()
        total = len(eligible)
        self._logger.info(
            "Of which %d are eligible for deletion (%s)",
            total,
            convert_filesize(folder_size))
        deleted = 0
        for dataset in eligible:
            try:
                if self.delete_user_copy(dataset):
                    deleted += 1
            except Exception as err: #pylint: disable=broad-except
                dataset.cmd_output += str(err)
                dataset.deletion_success = False
                dataset.date_deleted = timezone.now()
                dataset.save()
                self._logger.error("Failed to delete dataset")
                self._logger.debug(err)
        return (deleted, total)

    def delete_user_copy(self, copy):
        """
            Delete the data on disk for the copy object specified
            :param UserCopy copy: The database entry describing the copy
            :return boolean: was deletion success
        """
        try:
            with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
                if not copy.deletion_eligible():
                    self._logger.error("Not yet eligible for deletion")
                    return False
                shutil.rmtree(copy.folder_name())
                copy.deletion_success = True
                copy.date_deleted = timezone.now()
                copy.save()
                self._logger.debug("Deleted %s", copy.folder_name())
                with open(copy.changelog_file_name(), "a") as f_handle:
                    f_handle.write("{}\t {} deleted\n".format(
                        timezone.now(),
                        copy.folder_name().name))
                return True
        except TimeoutError:
            self._logger.critical("Unable to get DB lock")
            return False

    def process_copy_queue(self):
        """
            Work through the queue of copies to be craeted and do it
        """
        queue = UserCopy.objects.filter(date_copied__isnull=True)
        total = queue.count()
        self._logger.info("Datasets to copy: %d", total)
        copied = 0
        for copy in queue:
            try:
                if self.copy_to_userspace(copy):
                    copied += 1
            except Exception as err: #pylint: disable=broad-except
                copy.cmd_output += "\n" + str(err)
                copy.copy_success = False
                copy.date_copied = timezone.now()
                copy.save()
                self._logger.error("Copy failed")
                self._logger.debug(str(err))
        return (copied, total)

    def copy_to_userspace(self, copy):
        """
            Actually create the files on disk requested by the copy object
            :param UserCopy copy: The metadata describing the desired dataset in the copy
            :return boolean: Was operation successful
        """
        username = copy.username
        scan = copy.scan
        self._logger.debug("Username: %s", username)
        self._logger.debug("Scan: %s", scan)
        if copy.date_copied:
            self._logger.error("This copy request has already been processed")
            copy.cmd_output += "\n Attempted again {}".format(timezone.now())
            copy.save()
            return False
        user_folder = Path(settings.USER_DATA_FOLDER, username)
        self._logger.debug("User folder: %s", user_folder)
        if not (copy.include_raw_data or copy.include_recon_data):
            copy.cmd_output = "No data selected for copying"
            copy.copy_success = True
            copy.date_copied = timezone.now()
            copy.save()
            return False
        try:
            with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
                if not user_folder.exists():
                    self._logger.info("Need to create user folder")
                    if not Path(settings.CREATE_FOLDER_SCRIPT).exists():
                        self._logger.critical("Unable to find script to create folder")
                        copy.copy_success = False
                        copy.cmd_output = "Unable to find folder creation script"
                        copy.date_copied = timezone.now()
                        copy.save()
                        return False
                    try:
                        subprocess.run(
                            [
                                "sudo", settings.CREATE_FOLDER_SCRIPT, username,
                                settings.USER_DATA_FOLDER],
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                    except subprocess.CalledProcessError as err:
                        self._logger.error(err)
                        copy.copy_success = False
                        copy.cmd_output = (
                            "User folder creation script failed\n" + err.stdout
                            + "\n" + err.stderr
                        )
                        copy.date_copied = timezone.now()
                        copy.save()
                        return False
                dest_folder = copy.folder_name()
                self._logger.debug("Destination folder = %s", dest_folder)
                dest_folder.mkdir()
                success = True
                output = ""
                parser = self._lookup_parser(Path(scan.filename).suffix)
                if copy.include_recon_data:
                    (status, tmp_output) = parser.copy_recon(
                        scan, dest_folder, not copy.include_raw_data)
                    success &= status
                    output += tmp_output
                    if status:
                        self._logger.debug("Reconstructed data copied")
                    else:
                        self._logger.error("Failed to copy reconstructed data")
                if not copy.include_raw_data and success:
                    #not including raw so won't have sample info txt file without extra work
                    sample_info_file = scan.sample_info_filename()
                    shutil.copy(sample_info_file, dest_folder)
                if copy.include_raw_data and success: # only attempt if the previous step worked
                    (status, tmp_output) = parser.copy_raw(scan, dest_folder)
                    success &= status
                    output += tmp_output
                    if status:
                        self._logger.debug("Raw data copied")
                    else: self._logger.error("Failed to copy raw data")
                self._copy_user_readme_file(dest_folder)
                if not success: # need to roll back to ensure we don't leave stuff on the fs
                    self._logger.warning("Copy failed deleting folder")
                    output += "Copy failed, deleting folder\n"
                    shutil.rmtree(dest_folder)
                copy.copy_success = success
                copy.date_copied = timezone.now()
                copy.cmd_output = output
                if success:
                    self._generate_copy_info_file(copy)
                    with open(copy.changelog_file_name(), "a") as f_handle:
                        f_handle.write("{}\t {} created\n".format(
                            timezone.now(),
                            copy.folder_name().name))
            copy.save()
            return success
        except TimeoutError:
            self._logger.critical("Unable to get DB lock")
            return False

    def _generate_copy_info_file(self, copy):
        self._logger.debug("Generating info file for copy")
        filename = Path(copy.folder_name(), "INFO.txt")
        self._logger.debug("Filename: %s", filename)
        with open(filename, "w") as f_handle:
            f_handle.write("Original folder name: {}\r\n".format(
                Path(copy.scan.path).name))
            f_handle.write("Data copy request number: {}\r\n".format(copy.pk))
            f_handle.write(
                "Data available until at least {}. After this time it may be deleted.\r\n".format(
                    copy.deletion_valid_from()))

    def _copy_user_readme_file(self, destination):
        readme_dst = Path(destination, "README.txt")
        self._logger.debug("Path for readme file: %s", readme_dst)
        if readme_dst.exists():
            self._logger.warning("README file already exists NOT copying file in")
            return False
        src = Path(settings.BASE_DIR, settings.USER_COPY_SCAN_README)
        self._logger.debug("Copying file from %s", src)
        shutil.copy(src, readme_dst)
        return True

    def usage_threshold_exceeded(self, threshold, mnt_point=Path(settings.USER_DATA_FOLDER)):  #pylint: disable=(no-self-use
        """
            Check that the specified percentage of the disk space is free
            :param float threshold: The threshold to compare against
            :param Path: The mount point to check
            :return boolean
        """
        return threshold > mount_free_percent(mnt_point)
