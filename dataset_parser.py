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
    Philip Basford
"""

from abc import ABC, abstractmethod
import logging
import subprocess
from pathlib import Path

class DatasetParser(ABC):
    """
        Abstract class the all other parsers inherit from
        Describes the basic functionality that must be implemented and provies some helper methods
    """
    def __init__(self, log_level=logging.WARN):
        self._logger = logging.getLogger("Dataset Parser")
        self._logger.setLevel(log_level)

    @abstractmethod
    def extensions(self):
        """
            Returns a list of extensions that the parser knows about
        """

    @abstractmethod
    def process_file(self, dataset, scan_data=None):
        """
            Process the specified file and add to database
            :param Path dataset: Where to find the dataset
            :param Scan scan_data: The object to insert the data into
        """

    @abstractmethod
    def process_associated_files(self, db_entry):
        """
            Process any other files that might contain data about the scan
        """

    @abstractmethod
    def list_files(self, directory):
        """
            Return a list of all the files in the specified directory that can be parsed
            :param Path directory: Where to look
            :return List: the files found
        """

    def _list_files(self, directory, extensions):
        """
            List all the files with the specified extensions
            :param Path directory: Where to look
            :param List extensions: The extensions to include in the list
            :return List: the files found
        """
        if not directory.exists():
            raise ValueError("Path must exist")
        all_files = []
        if ".tif" in extensions:
            output = subprocess.run(f"find '{directory}/' -type f",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        else:
            self._logger.debug("Searching %s for non-tif files", directory)
            output = subprocess.run(f"find '{directory}/' -type f  -not -name *.tif",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        all_files = output.stdout.decode("utf-8").split("\n")
        self._logger.debug("found %d files", len(all_files))
        files = []
        for ext in extensions:
            self._logger.debug("Looking for %s files", ext)
            new_files = []
            for f_name in all_files:
                if f_name.endswith(ext):
                    new_files.append(Path(f_name))
            self._logger.info("Found %d files with extension %s", len(new_files), ext)
            files += new_files
        self._logger.info("Found %d files in total", len(files))
        return files


    @abstractmethod
    def get_model(self):
        """
            Return the model for the data to be stored in
            :return Scan
        """
    @abstractmethod
    def copy_raw(self, scan, destination):
        """
            Copy the raw data to the destination
            :param Scan scan: The scan to copy
            :param Path destination: Where to copy to
            :return (status, output)
        """

    @abstractmethod
    def copy_recon(self, scan, destination, include_metadata=False):
        """
            Copy the reconstructed data to the destination
            :param Scan scan: The scan to copy
            :param Path destination: Where to copy to
            :param boolean include_metadata: Should meta data files be copied across
            :return (status, output)
        """
