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

    Details of all the parameters in Nikon xtekct and xtekhelixct files
    to be parsed into the system
"""
XTEKCT_MODE = 1
XTEKHELIX_MODE = 2

CT_SECTION = "XTekCT"
HELIX_SECTION = "XTekHelixCT"
CTPRO_SECTION = "CTPro"
XRAY_SECTION = "Xrays"
DICOM_SECTION = "DICOM"
SCATTER_SECTION = "ScatterCorrection"

def get_xtek_param_list(mode=XTEKCT_MODE):
    """
        Return the list of parameters to parse from the file
        target, type, section, source

        :param mode: The mode should either be XTEKCT_MODE OR XTEKHELIX_MODE
        :returns list. parameters to read in.
    """
    if mode == XTEKCT_MODE:
        scan_data_section = CT_SECTION
    elif mode == XTEKHELIX_MODE:
        scan_data_section = HELIX_SECTION
    else:
        raise ValueError("Unknown mode: {}".format(mode))
    #Target, Type, Section, Source
    params = [
        ["name", "string", scan_data_section, "Name"],
        ["operator_id", "string", scan_data_section, "OperatorID"],
        ["input_separator", "string", scan_data_section, "InputSeparator"],
        ["output_separator", "string", scan_data_section, "OutputSeparator"],
        ["input_folder_name", "string", scan_data_section, "InputFolderName"],
        ["output_folder_name", "string", scan_data_section, "OutputFolderName"],
        ["voxels_x", "int", scan_data_section, "VoxelsX"],
        ["voxels_y", "int", scan_data_section, "VoxelsY"],
        ["voxels_z", "int", scan_data_section, "VoxelsZ"],
        ["voxel_size_x", "float", scan_data_section, "VoxelSizeX"],
        ["voxel_size_y", "float", scan_data_section, "VoxelSizeY"],
        ["voxel_size_z", "float", scan_data_section, "VoxelSizeZ"],
        ["offset_x", "float", scan_data_section, "OffsetX"],
        ["offset_y", "float", scan_data_section, "OffsetY"],
        ["offset_z", "float", scan_data_section, "OffsetZ"],
        ["src_to_object", "float", scan_data_section, "SrcToObject"],
        ["src_to_detector", "float", scan_data_section, "SrcToDetector"],
        ["mask_radius", "float", scan_data_section, "MaskRadius"],
        ["detector_pixels_x", "int", scan_data_section, "DetectorPixelsX"],
        ["detector_pixels_y", "int", scan_data_section, "DetectorPixelsY"],
        ["detector_pixel_size_x", "float", scan_data_section, "DetectorPixelSizeX"],
        ["detector_pixel_size_y", "float", scan_data_section, "DetectorPixelSizeY"],
        ["detector_offset_x", "float", scan_data_section, "DetectorOffsetX"],
        ["detector_offset_y", "float", scan_data_section, "DetectorOffsetY"],
        ["centre_of_rotation_top", "float", scan_data_section, "CentreOfRotationTop"],
        ["centre_of_rotation_bottom", "float", scan_data_section, "CentreOfRotationBottom"],
        ["white_level", "int", scan_data_section, "WhiteLevel"],
        ["scattering", "float", scan_data_section, "Scattering"],
        ["beam_hardening_lut_file", "string", scan_data_section, "BeamHardeningLUTFile"],
        ["coef_x4", "float", scan_data_section, "CoefX4"],
        ["coef_x3", "float", scan_data_section, "CoefX3"],
        ["coef_x2", "float", scan_data_section, "CoefX2"],
        ["coef_x1", "float", scan_data_section, "CoefX1"],
        ["coef_x0", "float", scan_data_section, "CoefX0"],
        ["scale", "float", scan_data_section, "Scale"],
        ["region_start_x", "int", scan_data_section, "RegionStartX"],
        ["region_start_y", "int", scan_data_section, "RegionStartY"],
        ["region_pixels_x", "int", scan_data_section, "RegionPixelsX"],
        ["region_pixels_y", "int", scan_data_section, "RegionPixelsY"],
        ["projections", "int", scan_data_section, "Projections"],
        ["initial_angle", "float", scan_data_section, "InitialAngle"],
        ["angular_step", "float", scan_data_section, "AngularStep"],
        ["interpolation_type", "int", scan_data_section, "InterpolationType"],
        ["filter_type", "int", scan_data_section, "FilterType"],
        ["cutoff_frequency", "float", scan_data_section, "CutOffFrequency"],
        ["exponent", "float", scan_data_section, "Exponent"],
        ["normalisation", "float", scan_data_section, "Normalisation"],
        ["median_filter_kernel_size", "int", scan_data_section, "MedianFilterKernelSize"],
        ["convolution_kernel_size", "int", scan_data_section, "ConvolutionKernelSize"],
        ["scaling", "float", scan_data_section, "Scaling"],
        ["output_units", "string", scan_data_section, "OutputUnits"],
        ["units", "string", scan_data_section, "Units"],
        ["automatic_centre_of_rotation", "int", scan_data_section, "AutomaticCentreOfRotation"],
        ["automatic_centre_of_rotation_offset_z1", "float", scan_data_section,
         "AutomaticCentreOfRotationOffsetZ1"],
        ["automatic_centre_of_rotation_offset_z2", "float", scan_data_section,
         "AutomaticCentreOfRotationOffsetZ2"],
        ["automatic_centre_of_rotation_mask_radius", "float", scan_data_section,
         "AutomaticCentreOfRotationMaskRadius"],
        ["output_type", "int", scan_data_section, "OutputType"],
        ["import_conversion", "int", scan_data_section, "ImportConversion"],
        ["auto_scaling_type", "int", scan_data_section, "AutoScalingType"],
        ["scaling_minimum", "float", scan_data_section, "ScalingMinimum"],
        ["scaling_maximum", "float", scan_data_section, "ScalingMaximum"],
        ["low_percentile", "float", scan_data_section, "LowPercentile"],
        ["high_percentile", "float", scan_data_section, "HighPercentile"],
        ["object_offset_x", "float", scan_data_section, "ObjectOffsetX"],
        ["object_roll", "float", scan_data_section, "ObjectRoll"],
        ["object_offset_x_start", "float", scan_data_section, "ObjectOffsetXStart"],
        ["object_offset_x_end", "float", scan_data_section, "ObjectOffsetXEnd"],
        ["beam_hardening_preset", "int", CTPRO_SECTION, "BeamHardeningPreset"],
        ["filter_preset", "int", CTPRO_SECTION, "FilterPreset"],
        ["filter_thickness_mm", "float", CTPRO_SECTION, "Filter_ThicknessMM"],
        ["filter_material", "string", CTPRO_SECTION, "Filter_Material"],
        ["shuttling", "bool", CTPRO_SECTION, "Shuttling"],
        ["voxel_scaling_factor", "int", CTPRO_SECTION, "VoxelScalingFactor"],
        ["xray_kv", "int", XRAY_SECTION, "XraykV"],
        ["xray_ua", "int", XRAY_SECTION, "XrayuA"],
        ["dicom", "string", DICOM_SECTION, "DICOMTags"],
        ["modifier_id", "string", scan_data_section, "ModifierID"],
        ["input_name", "string", scan_data_section, "InputName"],
        ["input_digits", "int", scan_data_section, "InputDigits"],
        ["output_name", "string", scan_data_section, "OutputName"],
        ["output_digits", "int", scan_data_section, "OutputDigits"],
        ["virtual_detector_pixels_x", "int", scan_data_section, "VirtualDetectorPixelsX"],
        ["virtual_detector_pixels_y", "int", scan_data_section, "VirtualDetectorPixelsY"],
        ["virtual_detector_pixel_size_x", "float", scan_data_section, "VirtualDetectorPixelSizeX"],
        ["virtual_detector_pixel_size_y", "float", scan_data_section, "VirtualDetectorPixelSizeY"],
        ["virtual_detector_offset_x", "float", scan_data_section, "VirtualDetectorOffsetX"],
        ["virtual_detector_offset_y", "float", scan_data_section, "VirtualDetectorOffsetY"],
        ["src_to_virtual_detector", "float", scan_data_section, "SrcToVirtualDetector"],
        ["object_offset_y", "float", scan_data_section, "ObjectOffsetY"],
        ["object_tilt", "float", scan_data_section, "ObjectTilt"],
        ["blanking", "int", scan_data_section, "Blanking"],
        ["order_fft", "int", scan_data_section, "OrderFFT"],
        ["version", "string", CTPRO_SECTION, "Version"],
        ["product", "string", CTPRO_SECTION, "Product"],
        ["autocor_num_bands", "int", CTPRO_SECTION, "AutoCOR_NumBands"],
        ["cor_auto_accuracy", "int", CTPRO_SECTION, "CorAutoAccuracy"],
        ["slice_height_mm_single", "float", CTPRO_SECTION, "SliceHeightMMSingle"],
        ["slice_height_mm_dual_top", "float", CTPRO_SECTION, "SliceHeightMMDualTop"],
        ["slice_height_mm_dual_bottom", "float", CTPRO_SECTION, "SliceHeightMMDualBottom"],
        ["angle_file_use", "bool", CTPRO_SECTION, "AngleFile_Use"],
        ["angle_file_ignore_errors", "bool", CTPRO_SECTION, "AngleFile_IgnoreErrors"],
        ["timestamp_folder", "int", scan_data_section, "TimeStampFolder"],
        ["increment", "int", scan_data_section, "Increment"],
        ["veiling_glare_applied", "int", SCATTER_SECTION, "VeilingGlareApplied"],
    ]
    if mode == XTEKHELIX_MODE:
        params += [
            ["derivative_type", "int", HELIX_SECTION, "DerivativeType"],
            ["pitch", "float", HELIX_SECTION, "Pitch"],
            ["automatic_geometry", "int", HELIX_SECTION, "AutomaticGeometry"],
            ["automatic_geometry_increment", "int", HELIX_SECTION, "AutomaticGeometryIncrement"],
            ["automatic_geometry_binning", "int", HELIX_SECTION, "AutomaticGeometryBinning"],
            ["automatic_geometry_window", "int", HELIX_SECTION, "AutomaticGeometryWindow"],
        ]
    return params
