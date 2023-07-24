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
    
    Handle VSI files from the microscopes
"""
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from xrh_utils import (
    calculate_file_hash,
)


from scans.models import (
    OmeChannel,
    OmeData,
    OmeDetector,
    OmeImage,
    OmeObjective,
    OmePlane,
    ScanAttachment,
    ScanAttachmentType
)


from dataset_parser import DatasetParser

NS = {"ome":"http://www.openmicroscopy.org/Schemas/OME/2016-06"} # namespace within the XML to us
CONVERTER_COMMAND = "/opt/xrh-scripts/vsi_extractor.py"


class VsiParser(DatasetParser):
    """
        See dataset_parser.py for superclass
        Handle VSI files
    """
    EXTENSIONS = [".vsi"]

    def __init__(self, log_level=logging.WARN):
        super().__init__(log_level)
        self._logger = logging.getLogger("Vsi Parser")
        self._logger.level = log_level
        self._detectors = {}
        self._objectives = {}
        self._xml_root = None

    def extensions(self):
        return self.EXTENSIONS

    def get_model(self):
        return OmeData

    def list_files(self, directory):
        return super()._list_files(directory, self.EXTENSIONS)

    def _xml_file_name(self, dataset):
        """
            Work out what the xml filename will be for a given dataset name
            :param Path dataset: The name of the VSI dataset
        """
        self._logger.debug("VSI file: %s", dataset)
        dirname = dataset.parent
        self._logger.debug("Directory name: %s", dirname)
        xmlfile = Path(dirname, dataset.stem + ".xml")
        self._logger.debug("XML file name: %s", xmlfile)
        return xmlfile

    def _find_image_names(self):
        """
            Get a list of image names used in the file
            This works on the basis that each new image is the start of a new size pyramid
            and therefore is larger in pixel count that the previous image found
        """
        images = []
        last_size = 0
        for image in self._xml_root.findall("ome:Image", NS):
            pixels = image.find("ome:Pixels", NS)
            size_x = int(pixels.get("SizeX"))
            size_y = int(pixels.get("SizeY"))
            size = size_x * size_y
            if size > last_size:
                img_name = image.get("Name")
                if img_name == "macro image":
                    continue    #Handle this image seperately anyway
                images.append(image.get("Name"))
            last_size = size
        return images

    def _process_instruments(self):
        for instrument in self._xml_root.findall("ome:Instrument", NS):
            for detector_xml in instrument.findall("ome:Detector", NS):
                detector_id = detector_xml.attrib["ID"]
                try:
                    detector_gain = detector_xml.attrib["Gain"]
                except KeyError:
                    detector_gain = None
                    self._logger.warning("No detector gain found")
                detector_manufacturer = detector_xml.attrib["Manufacturer"]
                detector_model = detector_xml.attrib["Model"]
                try:
                    detector_serialno = detector_xml.attrib["SerialNumber"]
                except KeyError:
                    detector_serialno = None
                    self._logger.warning("No detector serial number found")
                try:
                    detector_type = detector_xml.attrib["Type"]
                except KeyError:
                    detector_type = None
                    self._logger.warning("No detector type found")
                detector = self._find_detector(
                    detector_manufacturer, detector_model, gain=detector_gain,
                    serial_number=detector_serialno, detector_type=detector_type)
                self._detectors[detector_id] = detector
            for objective_xml in instrument.findall("ome:Objective", NS):
                objective_model = objective_xml.attrib["Model"]
                objective_id = objective_xml.attrib["ID"]
                try:
                    objective_lens_na = objective_xml.attrib["LensNA"]
                except KeyError:
                    self._logger.warning("No LensNA found")
                    objective_lens_na = None
                if objective_xml.attrib["WorkingDistanceUnit"] != "µm":
                    self._logger.error(
                        "Unknown working distance unit %d",
                        objective_xml.attrib["WorkingDistanceUnit"])
                    raise ValueError("Unknown Unit")
                try:
                    objective_working_distance = float(objective_xml.attrib["WorkingDistance"])
                except KeyError:
                    self._logger.warning("No working distance found")
                    objective_working_distance = None
                try:
                    objective_nominal_magnification = float(
                        objective_xml.attrib["NominalMagnification"])
                except KeyError:
                    self._logger.warning("No nominal magnification found")
                    objective_nominal_magnification = None
                objective = self._find_objective(
                    objective_lens_na, objective_model,
                    objective_nominal_magnification, objective_working_distance)
                self._objectives[objective_id] = objective

    def _find_scanning_time(self, name=None):
        annotations = self._xml_root.find(
            "ome:StructuredAnnotations", NS).findall("ome:XMLAnnotation", NS)
        if name:
            self._logger.debug("Looking for scanning time for image %s", name)
            search_term = "{} Scanning Time (seconds)".format(name)
            self._logger.debug("Search term = %s", search_term)
            for annotation in annotations:
                if (
                        annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS)
                        .find("ome:Key", NS).text.startswith(search_term)):
                    return float(
                        annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS).
                        find("ome:Value", NS).text.strip("[]"))
            self._logger.warning("Failed to find scan time for %s", name)
            return -1
        self._logger.debug("Looking for scanning time")
        count = 0
        for annotation in annotations:
            count += 1
            if annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS) \
                    .find("ome:Key", NS).text == "Scanning Time (seconds)":
                return float(
                    annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS).
                    find("ome:Value", NS).text.strip("[]"))
        self._logger.warning("Failed to find scan time for file in %d annotations", count)
        return -1

    def _find_channel_exposure_time_fix(self, image, channel=None):
        """
            Look in the structured annotations to find the correct exposure time
            :param string image: The name of the image to find the exposure time for
            :param string channel: The nameof the channel to find the exposure time for
            :return int: The exposure time (s)(negative if unable to find it)
        """
        annotations = self._xml_root.find("ome:StructuredAnnotations", NS) \
            .findall("ome:XMLAnnotation", NS)
        exposure = None
        if not channel or channel == "":
            search_string = "{} Microscope Exposure time (microseconds)".format(image)
            self._logger.debug("No channel name specified, searching for %s", search_string)
            for annotation in annotations:
                if (annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS)
                        .find("ome:Key", NS).text.startswith(search_string)):
                    exposure = float(annotation.find("ome:Value", NS) \
                        .find("ome:OriginalMetadata", NS)
                    .find("ome:Value", NS).text)
                    break
        else:
            self._logger.debug(
                "Looking for exposure time for channel %s in image %s", channel, image)
            search_string = "{} Channel name".format(image)
            self._logger.debug("Search string: %s", search_string)
            target_id = None
            for annotation in annotations:
                if(annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS)
                        .find("ome:Value", NS).text == channel):
                    key = annotation.find("ome:Value", NS).find(
                        "ome:OriginalMetadata", NS).find("ome:Key", NS).text
                    if search_string in key:
                        target_id = key.split()[-1]
                        break
            if not target_id:
                self._logger.warning("Failed to find exposure time for %s", search_string)
                return -2
            search_string = "{} Microscope Exposure time (microseconds) {}".format(image, target_id)
            self._logger.debug("Search string: %s", search_string)
            for annotation in annotations:
                if (annotation.find("ome:Value", NS).find("ome:OriginalMetadata", NS)
                        .find("ome:Key", NS).text == search_string):
                    exposure = float(annotation.find("ome:Value", NS) \
                        .find("ome:OriginalMetadata", NS)
                        .find("ome:Value", NS).text)
        if exposure:
            self._logger.debug("Found exposure %d microseconds", exposure)
            return exposure / 1000000
        self._logger.warning("Unable to find exposure time for %s", search_string)
        return -3


    def _process_image(self, name, scan_data):
        try:
            image_obj = OmeImage.objects.get(scan=scan_data, name=name)
            self._logger.debug("Found existing object (%d)", image_obj.pk)
        except ObjectDoesNotExist:
            image_obj = OmeImage()
            image_obj.scan = scan_data
            image_obj.name = name
        image_xml = None
        for image in self._xml_root.findall("ome:Image", NS):
            if image.get("Name") == name:
                image_xml = image
                break
        if image_xml is None:
            raise ValueError("Unable to find image with required name")
        image_obj.image_id = image_xml.get("ID")
        image_obj.objective = self._objectives[
            image_xml.find("ome:ObjectiveSettings", NS).attrib["ID"]]
        image_obj.refractive_index = float(
            image_xml.find("ome:ObjectiveSettings", NS).attrib["RefractiveIndex"])
        pixels_xml = image_xml.find("ome:Pixels", NS)
        image_obj.pixels_big_endian = bool(pixels_xml.attrib["BigEndian"])
        image_obj.pixels_dimension_order = pixels_xml.attrib["DimensionOrder"]
        image_obj.pixels_interleaved = bool(pixels_xml.attrib["Interleaved"])
        image_obj.pixels_significant_bits = int(pixels_xml.attrib["SignificantBits"])
        image_obj.pixels_type = pixels_xml.attrib["Type"]
        if (
                pixels_xml.attrib["PhysicalSizeXUnit"] != "µm" or
                pixels_xml.attrib["PhysicalSizeYUnit"] != "µm"):
            self._logger.error("Unrecognised unit")
            raise ValueError("Physical Size unrecognised unit")
        image_obj.physical_size_x = float(pixels_xml.attrib["PhysicalSizeX"])
        image_obj.physical_size_y = float(pixels_xml.attrib["PhysicalSizeY"])
        image_obj.pixels_x = int(pixels_xml.attrib["SizeX"])
        image_obj.pixels_y = int(pixels_xml.attrib["SizeY"])
        image_obj.size_t = int(pixels_xml.attrib["SizeT"])
        image_obj.size_c = int(pixels_xml.attrib["SizeC"])
        image_obj.size_z = int(pixels_xml.attrib["SizeZ"])
        image_obj.filename = "{}_{}_{}x{}.tif".format(
            scan_data.full_path().stem,
            name,
            image_obj.pixels_x,
            image_obj.pixels_y)
        image_obj.scan_time = self._find_scanning_time(name)
        image_obj.save()    #generate PK for image object so other things can link to it
        channels = {}
        for channel_xml in pixels_xml.findall("ome:Channel", NS):
            try:
                channel_name = channel_xml.attrib["Name"]
            except KeyError:
                channel_name = None
            channel_id = channel_xml.attrib["ID"]
            try:
                if channel_xml.attrib["EmissionWavelengthUnit"] != "nm":
                    self._logger.error("Unknown unit")
                    raise ValueError("Emission Wavelength unknown unit")
                channel_emmision_wavelength = channel_xml.attrib["EmissionWavelength"]
            except KeyError:
                channel_emmision_wavelength = None
            channel_detector_settings = channel_xml.find("ome:DetectorSettings", NS).attrib
            channel_binning = channel_detector_settings["Binning"]
            channel_detector = self._detectors[channel_detector_settings["ID"]]
            try:
                channel_detector_gain = float(channel_detector_settings["Gain"])
            except KeyError:
                channel_detector_gain = None
            channel_samples_per_pixel = int(channel_xml.attrib["SamplesPerPixel"])
            channel = self._find_channel(
                channel_name, channel_id, channel_emmision_wavelength,
                channel_binning, channel_detector, channel_detector_gain, channel_samples_per_pixel)
            channels[channel_id.split(":")[-1]] = channel
        self._logger.info("Processed %d channels", len(channels))
        for plane_xml in pixels_xml.findall("ome:Plane", NS):
            plane_channel = channels[plane_xml.attrib["TheC"]]
            channel_name = plane_channel.name
            self._logger.debug("Plane channel name %s", channel_name)
            image_name = image_obj.name
            self._logger.debug("Image name %s", image_name)
            plane_exposure = self._find_channel_exposure_time_fix(image_name, channel_name)
            if plane_exposure < 0:
                plane_exposure = None
            if (
                    plane_xml.attrib["PositionXUnit"] != "µm" or
                    plane_xml.attrib["PositionYUnit"] != "µm"):
                self._logger.error("Position unrecognised unit")
                raise ValueError("Position unrecognised unit")
            plane_position_x = float(plane_xml.attrib["PositionX"])
            plane_position_y = float(plane_xml.attrib["PositionY"])
            plane_z = int(plane_xml.attrib["TheZ"])
            plane_t = int(plane_xml.attrib["TheT"])
            plane = self._find_plane(
                plane_channel, plane_exposure, plane_position_x,
                plane_position_y, plane_z, plane_t, image_obj)
            self._save_plane_images(plane)
        image_obj.save()
        return image_obj

    def _save_plane_images(self, plane):
        self._logger.debug("Saving images for plane %s", plane)
        image_obj = plane.image
        channel_no = int(plane.channel.channel_id.split(":")[-1][0])
        self._logger.debug("Channel number %d", channel_no)
        path = image_obj.scan.full_path().parent
        self._logger.debug("File path: %s", path)
        fname_base = image_obj.scan.full_path().stem + "_" + image_obj.name
        self._logger.debug("Base fname: %s", fname_base)
        if not bool(plane.preview):
            preview_fname = "{}_ch{}_preview.png".format(fname_base, channel_no)
            self._logger.debug("Preview filename: %s", preview_fname)
            plane.preview.save(preview_fname, open(Path(path, preview_fname), "rb"))
        if not bool(plane.filename):
            tiff_fname = "{}_{}_{}_ch{}.tif".format(
                fname_base,
                image_obj.pixels_x,
                image_obj.pixels_y,
                channel_no)
            self._logger.debug("Tif filename: %s", tiff_fname)
            plane.filename = tiff_fname
        plane.save()

    def process_file(self, dataset, scan_data=None):
        if not scan_data:
            raise ValueError("scan_data must be passed in")
        self._logger.debug("Reading VSI file: %s", dataset)
        dirname = dataset.parent
        self._logger.debug("Directory name: %s", dirname)
        xmlfile = self._xml_file_name(dataset)
        self._logger.debug("XML file name: %s", xmlfile)
        if not xmlfile.exists():
            self._logger.info("Need to generate XML file and tiffs")
            try:
                subprocess.run(
                    "{} {}".format(CONVERTER_COMMAND, str(dataset)),
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                self._logger.debug("VSI extracted")
            except subprocess.CalledProcessError as output:
                self._logger.error("Failed to process VSI file")
                self._logger.debug("STDOUT: %s", output.stdout)
                self._logger.debug("STDERR: %s", output.stderr)
                raise output
        self._xml_root = ET.parse(xmlfile).getroot()
        self._process_instruments()
        scan_data.name = dataset.stem
        for image_xml in self._xml_root.findall("ome:Image", NS):
            try:
                scan_data.scan_date = datetime.strptime(
                    image_xml.find("ome:AcquisitionDate", NS).text,
                    "%Y-%m-%dT%H:%M:%S")
                break
            except AttributeError:
                pass
        if not scan_data.scan_date:
            raise ValueError("Unable to find acquisition date")
        checksum = calculate_file_hash(dataset)
        self._logger.debug("File checksum: %s", checksum)
        scan_time = self._find_scanning_time()
        self._logger.debug("Found scanning time %f", scan_time)
        scan_data.scan_time = scan_time
        scan_data.checksum = checksum
        scan_data.save()
        img_names = self._find_image_names()
        self._logger.info("Found %d images to process", len(img_names))
        self._logger.debug("Images: %r", img_names)
        for name in img_names:
            self._logger.debug("Processing %s", name)
            img_obj = self._process_image(name, scan_data)
            self._store_preview(img_obj)
        return scan_data

    def _find_plane(#pylint: disable=invalid-name
            self, channel, exposure, position_x, position_y, z, t, img):
        """
            Find the plane object for with the required specs, create it if it doesn't exist
            :param OmeChannel channel: details about the channel used for imaging
            :param float exposure length of exposure for the image
            :param float position_x: x axis position
            :param float position_y: y axis position
            :param int z: Z position of plane
            :param int t: T position of plane
            :param OmeImage img, the image to look for the plane in
            :return OmePlane: Object with the required params
        """
        try:
            plane = img.omeplane_set.get(
                channel=channel,
                exposure=exposure,
                position_x=position_x,
                position_y=position_y,
                z=z,
                t=t)
            self._logger.debug("Found plane (%d)", plane.pk)
        except ObjectDoesNotExist:
            self._logger.debug("Failed to find plane")
            plane = OmePlane()
            plane.channel = channel
            plane.exposure = exposure
            plane.position_x = position_x
            plane.position_y = position_y
            plane.z = z
            plane.t = t
            plane.image = img
            plane.save()
            self._logger.debug("New plane saved (%d)", plane.pk)
        return plane

    def _find_objective(
            self, lens_na=None, model=None,
            nominal_magnification=None, working_distance=None):
        """
            Find the objective with the required params
            :param float len_na: (Default: None)
            :param string model: (Default:None)
            :param float nominal_magnification: (Default: None)
            :param float working_distance: (Default:None)
            :return OmeObjective: Object with the required params
        """
        try:
            objective = OmeObjective.objects.get(
                lens_na=lens_na,
                model=model,
                nominal_magnification=nominal_magnification,
                working_distance=working_distance)
            self._logger.debug("Found objective (%d)", objective.pk)
        except ObjectDoesNotExist:
            self._logger.warning("Failed to find objective")
            objective = OmeObjective(
                lens_na=lens_na,
                model=model,
                nominal_magnification=nominal_magnification,
                working_distance=working_distance)
            objective.save()
            self._logger.debug("New objective saved (%d)", objective.pk)
        return objective


    def _find_channel(
            self, name, channel_id, emission_wavelength,
            binning, detector, gain, samples_per_pixel=None):
        """
            Find the the specified channel in the DB create if it doesn't exist
            :param string name: The Channel name
            :param string channel_id: The Channel ID
            :param float emission_wavelength: wavelength of light used
            :param string binning: Details of the binning used eg. 1x1
            :param OmeDetector detector: The detector object used
            :param float gain: The gain used
            :param int samples_per_pixel: Number of samples taken
        """
        try:
            channel = OmeChannel.objects.get(
                name=name, channel_id=channel_id, emission_wavelength=emission_wavelength,
                samples_per_pixel=samples_per_pixel, detector=detector, detector_gain=gain,
                binning=binning)
            self._logger.debug("Found channel (%d)", channel.pk)
        except ObjectDoesNotExist:
            self._logger.warning("Failed to find channel")
            channel = OmeChannel(
                name=name, emission_wavelength=emission_wavelength,
                samples_per_pixel=samples_per_pixel, channel_id=channel_id, detector=detector,
                detector_gain=gain, binning=binning)
            channel.save()
            self._logger.debug("Created channel (%d)", channel.pk)
        return channel


    def _find_detector(
            self, manufacturer, model, gain,
            serial_number=None, detector_type=None):
        """
            Find the detector record create it if it doesn't exist
            :param string manufacturer:
            :param string model:
            :param float gain:
            :param string serial_number:
            :param string detector_type:
            :returns OmeDetector
        """
        try:
            detector = OmeDetector.objects.get(
                manufacturer=manufacturer, model=model, gain=gain,
                serial_number=serial_number, detector_type=detector_type)
            self._logger.debug("Found detector (%d)", detector.pk)
        except ObjectDoesNotExist:
            self._logger.warning("Failed to find detector")
            detector = OmeDetector(
                manufacturer=manufacturer, model=model, gain=gain,
                serial_number=serial_number, detector_type=detector_type)
            detector.save()
            self._logger.debug("Created detector (%d)", detector.pk)
        return detector

    def process_associated_files(self, db_entry):
        self._logger.debug("Processing associated files")
        self._store_overview(db_entry)
        self._store_vsi(db_entry)
        self._store_xml(db_entry)

    def _store_vsi(self, scan_entry):
        """
            Add the VSI file into the mangement system
            :param Scan scan_entry: The db record for the scan entry
        """
        fname = scan_entry.full_path()
        name = fname.name
        self._logger.debug("VSI file: %s", fname)
        if fname.exists():
            self._logger.debug("VSI found")
            vsi_checksum = calculate_file_hash(fname)
            attachment_type = ScanAttachmentType.objects.get(name="VSI File")
            try:
                vsi_file_entry = ScanAttachment.objects.get(
                    scan=scan_entry,
                    attachment_type=attachment_type)
            except ObjectDoesNotExist:
                vsi_file_entry = ScanAttachment(
                    scan=scan_entry,
                    attachment_type=attachment_type,
                    name=name,
                    checksum=vsi_checksum)
                vsi_file_entry.checksum = vsi_checksum
                vsi_file_entry.editable = False
            if vsi_checksum != vsi_file_entry.checksum:
                self._logger.debug("VSI checksum: BAD")
                vsi_file_entry.checksum = vsi_checksum
                vsi_file_entry.attachment.delete(save=False)
                vsi_file_entry.attachment.save(name, open(fname, "r"))
            else:
                self._logger.debug("VSI checksum_ OK")
            vsi_file_entry.save()


    def _store_xml(self, scan_entry):
        """
            Store the generated OME XML file into the management system
            :param Scan scan_entry: The db record for the scan entry
        """
        xml_file = self._xml_file_name(scan_entry.full_path())
        name = xml_file.name
        self._logger.debug("XML file: %s", xml_file)
        if xml_file.exists():
            self._logger.debug("XML found")
            xml_checksum = calculate_file_hash(xml_file)
            attachment_type = ScanAttachmentType.objects.get(name="OME XML")
            try:
                xml_file_entry = ScanAttachment.objects.get(
                    scan=scan_entry,
                    attachment_type=attachment_type)
            except ObjectDoesNotExist:
                xml_file_entry = ScanAttachment(
                    scan=scan_entry,
                    attachment_type=attachment_type,
                    name=name,
                    checksum=xml_checksum)
                xml_file_entry.editable = False
                xml_file_entry.attachment.save(name, open(xml_file, "r"))
            if xml_checksum != xml_file_entry.checksum:
                self._logger.debug("XML checksum: BAD")
                xml_file_entry.checksum = xml_checksum
                xml_file_entry.attachment.delete(save=False)
                xml_file_entry.attachment.save(name, open(xml_file, "r"))
            else:
                self._logger.debug("XML checksum: OK")
            xml_file_entry.save()



    def _store_overview(self, scan_entry):
        """
            Store the overview image
            :param Scan scan_entry: The db record for the scan entry
        """
        if scan_entry.overview.name is None or scan_entry.overview.name == '':
            vsi_fname = scan_entry.full_path()
            self._logger.debug("VSI file: %s", vsi_fname)
            dir_name = vsi_fname.parent
            base_name = vsi_fname.stem
            overview_fname = Path(dir_name, base_name + "_macro.png")
            self._logger.debug("Overview file: %s", overview_fname)
            if not overview_fname.exists():
                self._logger.error("Overview file doesn't exist")
                return
            self._logger.debug("Found overview file")
            scan_entry.overview.save(overview_fname.name, open(overview_fname, "rb"))


    def _store_preview(self, image_entry):
        """
            Store the preview image
            :param OmeImage image_entry: The db record for the image entry
        """
        if image_entry.preview.name is None or image_entry.preview.name == '':
            scan_entry = image_entry.scan
            vsi_fname = scan_entry.full_path()
            self._logger.debug("VSI file: %s", vsi_fname)
            dir_name = vsi_fname.parent
            base_name = vsi_fname.stem
            name = image_entry.name
            self._logger.debug("Image name %s", name)
            preview_fname = Path(dir_name, (base_name + "_" + name + "_preview.png"))
            self._logger.debug("Preview file: %s", preview_fname)
            if not preview_fname.exists():
                self._logger.error("Preview file doesn't exist")
                return
            self._logger.debug("Found preview file")
            image_entry.preview.save(preview_fname.name, open(preview_fname, "rb"))

    def copy_raw(self, scan, destination):
        raise NotImplementedError("Not yet written")

    def copy_recon(self, scan, destination):
        raise NotImplementedError("Not yet written")
