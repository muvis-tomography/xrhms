#pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, no-self-use
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
"""
import logging
from pathlib import Path
from datetime import timedelta
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from xrh_utils import directory_size

from .gain import Gain
from .nikon_scan_modes import SCAN_MODE_CONTINUOUS, SCAN_MODE_STANDARD, SCAN_MODE_MRA, \
    SCAN_MODE_HELICAL
from .nikon_target_metals import TARGET_METAL_CHOICES
from .scan import Scan



class NikonCTScan(Scan):
    """
        Stores details about a single scan performed
    """
    class Meta:
        verbose_name = "Nikon CT Scan"
        verbose_name_plural = "Nikon CT Scans"


    def get_subfolder(self):
        return [self.pk]

    operator_id = models.CharField( # seen on XRH scanner but not medX
        max_length=255,
        db_index=True,
        blank=True,
        null=True,
        verbose_name="Operator ID")
    input_separator = models.CharField(
        max_length=30,
        blank=True,
        null=True)
    input_folder_name = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True)
    output_separator = models.CharField(
        max_length=30,
        blank=True,
        null=True)
    output_folder_name = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True)
    voxels_x = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Voxels X")
    voxel_size_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Voxel size X")
    offset_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Offset X")
    voxels_y = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Voxels Y")
    voxel_size_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Voxel size Y")
    offset_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Offset Y")
    voxels_z = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Voxels Z")
    voxel_size_z = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Voxel size Z")
    offset_z = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Offset Z")
    mask_radius = models.FloatField(
        blank=True,
        null=True)
    detector_offset_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Detector offset X")
    detector_offset_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Detector offset Y")
    region_start_x = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Region start X")
    region_pixels_x = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Region pixels X")
    region_start_y = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Region start Y")
    region_pixels_y = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Region pixels Y")
    units = models.CharField(
        max_length=15,
        blank=True,
        null=True)
    scaling = models.FloatField(
        blank=True,
        null=True)
    output_units = models.CharField(
        max_length=15,
        blank=True,
        null=True)
    output_type = models.IntegerField(
        blank=True,
        null=True)
    import_conversion = models.IntegerField(
        blank=True,
        null=True)
    auto_scaling_type = models.IntegerField(
        blank=True,
        null=True)
    scaling_minimum = models.FloatField(
        blank=True,
        null=True)
    scaling_maximum = models.FloatField(
        blank=True,
        null=True)
    low_percentile = models.FloatField(
        blank=True,
        null=True)
    high_percentile = models.FloatField(
        blank=True,
        null=True)
    angular_step = models.FloatField(
        blank=True,
        null=True)
    centre_of_rotation_top = models.FloatField(
        blank=True,
        null=True)
    centre_of_rotation_bottom = models.FloatField(
        blank=True,
        null=True)
    white_level = models.IntegerField(
        blank=True,
        null=True)
    interpolation_type = models.IntegerField(
        blank=True,
        null=True)
    beam_hardening_lut_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Beam hardening LUT file")
    coef_x4 = models.FloatField(
        blank=True,
        null=True)
    coef_x3 = models.FloatField(
        blank=True,
        null=True)
    coef_x2 = models.FloatField(
        blank=True,
        null=True)
    coef_x1 = models.FloatField(
        blank=True,
        null=True)
    coef_x0 = models.FloatField(
        blank=True,
        null=True)
    scale = models.FloatField(
        blank=True,
        null=True)
    filter_type = models.IntegerField(
        blank=True,
        null=True)
    cutoff_frequency = models.FloatField(
        blank=True,
        null=True)
    exponent = models.FloatField(
        blank=True,
        null=True)
    normalisation = models.FloatField(
        blank=True,
        null=True)
    scattering = models.FloatField(
        blank=True,
        null=True)
    median_filter_kernel_size = models.IntegerField(
        blank=True,
        null=True)
    convolution_kernel_size = models.IntegerField(
        blank=True,
        null=True)
    filter_thickness_mm = models.IntegerField(
        blank=True,
        null=True)
    filter_material = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True)
    shuttling = models.BooleanField(
        blank=True,
        null=True)
    shuttling.boolean = False
    dicom = models.TextField(
        blank=True,
        null=True)
    exposure = models.IntegerField(
        blank=True,
        null=True)
    accumulation = models.IntegerField(
        blank=True,
        null=True)
    binning = models.IntegerField(
        blank=True,
        null=True)
    gain = models.IntegerField(
        blank=True,
        null=True)
    brightness = models.IntegerField(
        blank=True,
        null=True)
    digital_gain = models.IntegerField(
        blank=True,
        null=True)
    white_to_black_latency = models.IntegerField(
        blank=True,
        null=True)
    black_to_white_latency = models.IntegerField(
        blank=True,
        null=True)
    white_to_white_latency = models.IntegerField(
        blank=True,
        null=True)
    lines = models.IntegerField(
        blank=True,
        null=True)
    automatic_centre_of_rotation = models.IntegerField(
        blank=True,
        null=True)
    automatic_centre_of_rotation_offset_z1 = models.FloatField(
        blank=True,
        null=True)
    automatic_centre_of_rotation_offset_z2 = models.FloatField(
        blank=True,
        null=True)
    automatic_centre_of_rotation_mask_radius = models.FloatField(
        blank=True,
        null=True)
    filter_preset = models.IntegerField(
        blank=True,
        null=True)
    voxel_scaling_factor = models.IntegerField(
        blank=True,
        null=True)
    object_offset_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Object offset X")
    object_roll = models.FloatField(
        blank=True,
        null=True)
    beam_hardening_preset = models.IntegerField(
        blank=True,
        null=True)
    increment = models.IntegerField(
        blank=True,
        null=True)
    derivative_type = models.IntegerField(
        blank=True,
        null=True)
    pitch = models.FloatField(
        blank=True,
        null=True)
    automatic_geometry = models.IntegerField(
        blank=True,
        null=True)
    automatic_geometry_increment = models.IntegerField(
        blank=True,
        null=True)
    automatic_geometry_binning = models.IntegerField(
        blank=True,
        null=True)
    automatic_geometry_window = models.IntegerField(
        blank=True,
        null=True)
    object_offset_x_start = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Object offset X start")
    object_offset_x_end = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Object offset X end")
    #CT Pro fields below here
    modifier_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Modifier ID")
    input_name = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    input_digits = models.IntegerField(
        blank=True,
        null=True)
    output_name = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    output_digits = models.IntegerField(
        blank=True,
        null=True)
    virtual_detector_pixels_x = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Virtual detector pixels X")
    virtual_detector_pixels_y = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Virtual detector pixels Y")
    virtual_detector_pixel_size_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Virtual detector pixel size X")
    virtual_detector_pixel_size_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Virtual detector pixel size Y")
    virtual_detector_offset_x = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Virtual detector offset X")
    virtual_detector_offset_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Virtual detector offset Y")
    src_to_virtual_detector = models.FloatField(
        blank=True,
        null=True)
    object_offset_y = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Object offset Y")
    object_tilt = models.FloatField(
        blank=True,
        null=True)
    blanking = models.IntegerField(
        blank=True,
        null=True)
    order_fft = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Order FFT")
    version = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    product = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    autocor_num_bands = models.IntegerField(
        blank=True,
        null=True)
    cor_auto_accuracy = models.IntegerField(
        blank=True,
        null=True)
    slice_height_mm_single = models.FloatField(
        blank=True,
        null=True)
    slice_height_mm_dual_top = models.FloatField(
        blank=True,
        null=True)
    slice_height_mm_dual_bottom = models.FloatField(
        blank=True,
        null=True)
    angle_file_use = models.BooleanField(
        blank=True,
        null=True)
    angle_file_ignore_errors = models.BooleanField(
        blank=True,
        null=True)
    timestamp_folder = models.IntegerField(
        blank=True,
        null=True)
    xray_head = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="X-Ray head")
    target_metal = models.CharField(
        max_length=2,
        choices=TARGET_METAL_CHOICES,
        blank=True,
        null=True,
        help_text="The metal used in the multi-metal target")
    helical_continuous_scan = models.BooleanField(
        blank=True,
        null=True)
    helical_derivative_type = models.CharField(
        max_length=10,
        blank=True,
        null=True)
    helical_sample_top = models.FloatField(
        blank=True,
        null=True)
    helical_sample_bottom = models.FloatField(
        blank=True,
        null=True)
    helical_projections_per_rotation = models.IntegerField(
        blank=True,
        null=True)
    helical_upper_position_checked = models.BooleanField(
        blank=True,
        null=True)
    helical_lower_position_checked = models.BooleanField(
        blank=True,
        null=True)
    helical_upper_check_position = models.FloatField(
        blank=True,
        null=True)
    helical_lower_check_position = models.FloatField(
        blank=True,
        null=True)
    helical_upper_magnification_position = models.FloatField(
        blank=True,
        null=True)
    helical_lower_magnification_position = models.FloatField(
        blank=True,
        null=True)
    veiling_glare_applied = models.IntegerField(
        blank=True,
        null=True)
    max_pixels_to_shuttle = models.IntegerField(
        blank=True,
        null=True)

    def helical_rotations(self): #pylint: disable=inconsistent-return-statements
        if self.helical_projections_per_rotation:
            return float(self.projections) / self.helical_projections_per_rotation
        return

    def accumulation_readable(self):
        if self.accumulation is not None: # Can be 0 which would fail using if self.accumulation:
            return pow(2, self.accumulation)
        return "-"

    def estimate_time(self):
        try:
            time = (
                self.accumulation_readable() * self.projections *
                self.frames_per_projection * self.exposure / 1000)
            # time in seconds because exposure is given in milliseconds
            if self.shuttling:
                if not self.scanner.shuttle_multiplier:
                    logger = logging.getLogger(__name__)
                    logger.warning("No shuttle multiplier set for scanner %d", self.scanner_id)
                    time += self.projections
                else:
                    time += self.projections * self.scanner.shuttle_multiplier
            return timedelta(seconds=round(time, 0))
        except TypeError:
            #Something isn't available in the DB
            return None
    estimate_time.short_description = "Scan time estimation"

    def binning_readable(self):
        if self.binning == 0:
            return "1x"
        if self.binning == 1:
            return "2x"
        return "?"
    binning_readable.short_description = "Detector Binning"

    def analog_gain_readable(self):
        try:
            return self.scanner.gain_set.get(gain_type=Gain.ANALOG, index=self.gain).value
        except ObjectDoesNotExist:
            return None
    analog_gain_readable.short_description = "Analog Gain (dB)"

    def digital_gain_readable(self):
        try:
            return self.scanner.gain_set.get(gain_type=Gain.DIGITAL, index=self.digital_gain).value
        except ObjectDoesNotExist:
            return None

    digital_gain_readable.short_description = "Digital Gain (dB)"

    def scan_mode(self):
        if self.helical():
            return SCAN_MODE_HELICAL
        if self.shuttling and self.max_pixels_to_shuttle == 0:
            return SCAN_MODE_STANDARD
        if self.shuttling:
            return SCAN_MODE_MRA
        return SCAN_MODE_CONTINUOUS

    def helical(self):
        """
            The xtek file only has a pitch value if the scan was helical
        """
        return bool(self.pitch)
    helical.isboolean = True

    def proj90_index(self): #pylint: disable=inconsistent-return-statements
        """
            Return the number of the image for the 90 degree view
        """
        if self.helical():
            if self.helical_projections_per_rotation: #pylint: disable=no-else-return
                return int(self.helical_projections_per_rotation /4)
            else:
                return
        return int(self.projections / 4)

    def geometric_magnification(self):
        return round(self.detector_pixel_size_x / self.voxel_size_x, 3)

    def shuttling_text(self):
        if self.shuttling:
            return "Yes"
        return "No"
    shuttling_text.short_description = "Shuttling"

    def recon_directory(self):
        return Path(self.full_path().parent, Path(self.filename).stem)

    def recon_extra_dir(self):
        return Path(self.recon_directory(), settings.EXTRA_FOLDER)

    def recon_video_dir(self):
        return Path(self.recon_directory(), settings. VIDEO_FOLDER)

    def recon_size(self):
        recon_dir = self.recon_directory()
        return directory_size(recon_dir)

    def raw_files(self):
        path = Path(self.full_path()).parent
        base = Path(self.filename).stem
        filtered = []
        for item in path.glob("{}*".format(base)):
            if not item.is_dir():
                filtered.append(item)
        return filtered

    def raw_size(self):
        files = self.raw_files()
        size = 0
        for fname in files:
            size += fname.stat().st_size
        return size
