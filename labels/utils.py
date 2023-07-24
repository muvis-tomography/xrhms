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
    
    Utilities to help with printing labels
"""
from pathlib import Path
import subprocess
import logging
from labels.views import sample_label, archive_drive_label, project_label, address_label


LA62_PRINTER_11354 = "XRH_LabelWriter_450"
LB68_PRINTER_11354 = "Medx-labelWriter-450-left"
LB68_PRINTER_30321 = "Medx-labelWriter-450-right"

PRINTERS = [LA62_PRINTER_11354, LB68_PRINTER_11354, LB68_PRINTER_30321]

DEFAULT_PRINTER_NAME = LA62_PRINTER_11354

SAMPLE_LABEL_PRINTERS = {
    "LA62": LA62_PRINTER_11354,
    "LB68": LB68_PRINTER_11354
}

def print_address_label(contact, version=1, printer_name=LB68_PRINTER_30321):
    """
        Function to be called by web UI to print a label
        :param Contact contact: Who to print the address label for
        :param int version: which version of the label to print
        :param string printer_name: The printer to send the label to
    """
    logger = logging.getLogger("Address Label Printer")
    if printer_name not in PRINTERS:
        raise ValueError("Unknown printer")
    try:
        (temp_dir, filename) = address_label(contact, version=version)
    except ValueError as error:
        logger.error(error)
        return False
    label_file = Path(temp_dir.name, filename)
    status = _print(label_file, printer_name)
    logger.info("%s printed %r", Path(temp_dir.name, filename), status)
    return status



def print_sample_label(sample, version=1, printer_name=DEFAULT_PRINTER_NAME):
    """
        Function to be called by web UI to print a label
        :param Sample sample: the sample to print
        :param int version: which version of the label to print
        :param string printer_name: The printer to send the label to
    """
    logger = logging.getLogger("Sample Label Printer")
    if printer_name not in PRINTERS:
        raise ValueError("Unknown printer")
    (temp_dir, filename) = sample_label(sample, version=version)
    label_file = Path(temp_dir.name, filename)
    status = _print(label_file, printer_name)
    logger.info("%s printed %r", Path(temp_dir.name, filename), status)
    return status

def print_project_label(sample, version=1, printer_name=DEFAULT_PRINTER_NAME):
    """
        Function to be called by web UI to print a label
        :param Project project: the project to print
        :param int version: which version of the label to print
        :param string printer_name: The printer to send the label to
    """
    logger = logging.getLogger("Project Label Printer")
    if printer_name not in PRINTERS:
        raise ValueError("Unknown printer")
    (temp_dir, filename) = project_label(sample, version=version)
    label_file = Path(temp_dir.name, filename)
    status = _print(label_file, printer_name)
    logger.info("%s printed %r", Path(temp_dir.name, filename), status)
    return status

def _print(filename, printer_name=DEFAULT_PRINTER_NAME):
    """
        Send the generated label to the printer
        :param Path filename: The filename to submit to the printer
        :param string printer_name: The printer to send the label to
    """
    logger = logging.getLogger("Label Printer")
    if printer_name not in PRINTERS:
        raise ValueError("Unknown printer")
    cmd = ["lpr", "-P", printer_name, "-#", "1", "-h", str(filename)]
    logger.info("Command: %r", cmd)
    try:
        output = subprocess.run(
            cmd,
            shell=False,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as output:
        logger.error("Failed to submit job to lpr. Exit code (%d)", output.returncode)
        logger.error("STDOUT: %s", output.stdout)
        logger.error("STDERR: %s", output.stderr)
        return False
    return True

def print_drive_label(drive, version=1, printer_name=DEFAULT_PRINTER_NAME):
    """
        Function to be called by the UI to generate a label for archive disks
        :param ArchiveDrive drive: the drive to create the label for
        :param int version: which version of the label to print
        :param string printer_name: The printer to send the label to
    """
    logger = logging.getLogger("Drive Label Printer")
    if printer_name not in PRINTERS:
        raise ValueError("Unknown printer")
    (temp_dir, filename) = archive_drive_label(drive, version=version)
    label_file = Path(temp_dir.name, filename)
    status = _print(label_file, printer_name)
    logger.info("%s printed %r", Path(temp_dir.name, filename), status)
    return status
