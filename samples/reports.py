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

    Generate the PDF report for a sample
"""

from tempfile import TemporaryDirectory
from pathlib import Path
import logging
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import mark_safe
from django_mysql.locks import Lock
from django_mysql.exceptions import TimeoutError #pylint: disable=redefined-builtin
from weasyprint import HTML

from samples.models import SampleAttachmentType, SampleReport
from scans.models import ScanAttachmentType
from xrh_utils import video2thumbnail, compress_pdf
from xrhms.settings import BASE_DIR
IMG_WIDTH = "12cm"
IMG_WIDTH_2 = "8cm"
IMG_HEIGHT = "10cm"
OVERVIEW_HEIGHT = "4.5cm"
LOCK_NAME = "sample_report_generation_lock"
LOCK_TIMEOUT = 30

HEADER_IMG = Path(BASE_DIR + "/samples/templates/samples/header.png")

def generate_report(report, force=False, debug=False):
    """
        :param SampleReport report: The DB entry for the report
        :param boolean force: Regenerate it if it already exists
        :param boolean debug: Store extra files to make debuging easier
    """
    warnings = []
    errors = []
    logger = logging.getLogger("Sample report generater")
    logger.debug("Generating report number: %d", report.pk)
    logger.debug("Force: %r", force)
    logger.debug("Debug: %r", debug)
    if not force and report.date_generated:
        logger.warning("Report already generated")
        return None
    if force:
        logger.warning("Forcing generation of report")
    sample = report.sample
    xrh_id = sample.xrh_id()
    logger.debug("Sample ID: %s", xrh_id)
    project = report.project
    project_title = project.full_title
    if not project_title:
        logger.debug("Project title not set using name instead")
        warnings.append("No project title set - using name instead")
        project_title = project.name
    logger.debug("Project: %s (%d)", project_title, project.pk)
    try:
        status = sample.current_location()
    except (ObjectDoesNotExist, IndexError):
        warnings.append("No Status/location information available")
        status = None
    scan_list = report.reportscanmapping_set.all().order_by("scan__polymorphic_ctype", "scan__sample__xrh_id_suffix")
    temp_dir = TemporaryDirectory()
    logger.debug("Using temp dir: %s", temp_dir.name)
    generation_time = timezone.now()
    if sample.condition:
        condition = sample.condition.name
    else:
        condition = None
    if sample.storage_requirement:
        storage_requirements = sample.storage_requirement.name
    else:
        storage_requirements = None
    if sample.extraction_method:
        extraction_method = sample.extraction_method
    else:
        extraction_method = None
    try:
        pic_type = SampleAttachmentType.objects.get(name="Delivered photo front")
        pic = sample.sampleattachment_set.filter(attachment_type=pic_type)[0]
        delivered_pic_front = "file://{}".format(pic.attachment.path)
    except (ObjectDoesNotExist, IndexError):
        warnings.append("Unable to find delivered front photo of sample. Does it exist?")
        delivered_pic_front = None
    try:
        pic_type = SampleAttachmentType.objects.get(name="Delivered photo back")
        pic = sample.sampleattachment_set.filter(attachment_type=pic_type)[0]
        delivered_pic_back = "file://{}".format(pic.attachment.path)
    except (ObjectDoesNotExist, IndexError):
        warnings.append("Unable to find delivered back photo of sample. Does it exist?")
        delivered_pic_back = None
    returned_pic_front = None
    returned_pic_back = None
    if report.returned_photos:
        try:
            pic_type = SampleAttachmentType.objects.get(name="Returned photo front")
            pic = sample.sampleattachment_set.filter(attachment_type=pic_type)[0]
            returned_pic_front = "file://{}".format(pic.attachment.path)
        except (ObjectDoesNotExist, IndexError):
            warnings.append("Unable to find returned front photo of sample. Does it exist?")
        try:
            pic_type = SampleAttachmentType.objects.get(name="Returned photo back")
            pic = sample.sampleattachment_set.filter(attachment_type=pic_type)[0]
            returned_pic_back = "file://{}".format(pic.attachment.path)
        except (ObjectDoesNotExist, IndexError):
            warnings.append("Unable to find returned back photo of sample. Does it exist?")
    generic_photos = []
    if report.generic_photos:
        pic_type = SampleAttachmentType.objects.get(name="Generic photo")
        for photo in sample.sampleattachment_set.filter(attachment_type=pic_type):
            pic_details = {}
            pic_details["name"] = photo.name
            pic_details["notes"] = photo.notes
            pic_details["pic"] = "file://{}".format(photo.attachment.path)
            generic_photos.append(pic_details)
        if not generic_photos:
            warnings.append("Unable to find any generic photos")
    logger.debug("Report to contain %d generic photos", len(generic_photos))
    logger.debug("Report to contain %d scans", len(scan_list))
    scans = []
    for scan_map in scan_list:
        scan = scan_map.scan
        scan_details = {}
        scan_images = []
        scan_type = scan.scan_type()
        scan_details["type"] = scan_type
        scan_details["histology"] = []
        if scan_type == "Nikon CT Scan":
            scan_details["name"] = Path(scan.filename).stem
            scan_properties = {}
            scan_properties["Type"] = "CT Scan"
            scan_properties["Voxels X"] = scan.voxels_x
            scan_properties["Voxels Y"] = scan.voxels_y
            scan_properties["Voxels Z"] = scan.voxels_z
            scan_properties["Voxel size X"] = "{:.2f} µm".format(scan.voxel_size_x * 1000)
            scan_properties["Voxel size Y"] = "{:.2f} µm".format(scan.voxel_size_y * 1000)
            scan_properties["Voxel size Z"] = "{:.2f} µm".format(scan.voxel_size_z * 1000)
            scan_details["properties"] = scan_properties
            scan_params = {}
            scan_params["Scanner used"] = scan.scanner.name
            scan_params["Total scan time (approx)"] = str(scan.estimate_time())
            scan_params["Binning"] = scan.binning_readable()
            scan_params["Acceleration voltage"] = "{} kVp".format(scan.xray_kv)
            scan_params["Current"] = "{} µA".format(scan.xray_ua)
            scan_params["Power"] = "{:.2f} W".format(scan.power())
            scan_params["Angular projections"] = scan.projections
            scan_params["Frames per projection"] = scan.frames_per_projection
            scan_params["Exposure"] = "{} ms".format(scan.exposure)
            scan_params["Analog Gain"] = "{} dB".format(scan.analog_gain_readable())
            scan_params["X-Ray head"] = scan.xray_head
            if scan.target_metal:
                scan_params["Target metal"] = scan.get_target_metal_display
            scan_params["Filter material"] = scan.filter_material
            scan_params["Filter thickness"] = "{} mm".format(scan.filter_thickness_mm)
            if scan.shuttling:
                scan_params["Shuttling"] = "Yes"
            elif scan.shuttling is not None:
                scan_params["Shuttling"] = "No"
            scan_details["params"] = scan_params
            if report.projections:
                if scan.projection0deg_png:
                    projection_0 = {}
                    projection_0["name"] = "0 degree projection"
                    projection_0["url"] = "file://{}".format(scan.projection0deg_png.file)
                    projection_0["description"] = \
                        "Raw radiograph of the sample rotated to 0 degrees"
                    scan_images.append(projection_0)
                else:
                    warnings.append("Unable to find 0 degree projection")
                if scan.projection90deg_png:
                    projection_90 = {}
                    projection_90["name"] = "90 degree projection"
                    projection_90["url"] = "file://{}".format(scan.projection90deg_png.file)
                    projection_90["description"] = \
                        "Raw radiograph of the sample rotated to 90 degrees"
                    scan_images.append(projection_90)
                else:
                    warnings.append("Unable to find 90 degree projection")
            if report.xy_slice:
                if scan.xyslice_png:
                    xy_slice = {}
                    xy_slice["name"] = "XY slice"
                    xy_slice["url"] = "file://{}".format(scan.xyslice_png.file)
                    xy_slice["description"] = "XY slice though the volume"
                    scan_images.append(xy_slice)
                else:
                    warnings.append("Unable to find XY slice")
        elif scan_type == "Histology Slide":
            scan_params = {}
            scan_properties = {}
            scan_details["name"] = Path(scan.filename).stem
            scan_properties["Type"] = "Histology Image"
            scan_properties["Scanner used"] = scan.scanner.name
            scan_properties["Slide number"] = int(scan.sample.xrh_id_suffix)
            scan_properties["Total scan time"] = scan.scan_time_readable()
            if scan.staining:
                scan_properties["Staining Protocol"] = scan.staining
                scan_params["Staining Protocol"] = scan.staining.protocol
            if scan.staining_notes:
                scan_properties["Staining notes"] = mark_safe(
                    scan.staining_notes.replace("\n", "<br/>"))
            scan_details["properties"] = scan_properties
            scan_details["params"] = scan_params
            scan_overview = {}
            scan_overview["name"] = "Overview"
            scan_overview["url"] = "file://{}".format(scan.overview.file)
            scan_overview["description"] = "Overview of the scan"
            scan_images.append(scan_overview)
            scan_histology = []
            for image in scan.omeimage_set.all():
                logger.debug("Processing image %d", image.pk)
                histo = {}
                histo_params = {}
                histo["name"] = image.name
                histo["params"] = histo_params
                histo_params["Objective Magnification"] = image.objective_nominal_magnification()
                histo_params["Pixels Significant Bits"] = image.pixels_significant_bits
                histo_params["Physical Size X (µm)"] = round(image.physical_size_x, 3)
                histo_params["Physical Size Y (µm)"] = round(image.physical_size_y, 3)
                histo_params["Pixels X"] = image.pixels_x
                histo_params["Pixels Y"] = image.pixels_y
                histo_params["Image scan time"] = image.scan_time_readable()
                histo["image"] = "file://{}".format(image.preview.file)
                planes = []
                plane_set = image.omeplane_set.all()
                for plane in plane_set:
                    plane_params = {}
                    name = plane.channel.name
                    if not name:
                        name = "-"
                    plane_params["Name"] = name
                    plane_params["Exposure"] = plane.exposure
                    plane_params["Position X"] = round(plane.position_x, 3)
                    plane_params["Position Y"] = round(plane.position_y, 3)
                    wavelength = plane.channel.emission_wavelength
                    if not wavelength:
                        wavelength = "-"
                    plane_params["Wavelength (nm)"] = wavelength
                    if plane_set.count() > 1:
                        plane_image = "file://{}".format(plane.preview.file)
                    else:
                        plane_image = None
                    planes.append({"image": plane_image, "params" : plane_params})
                histo["planes"] = planes
                scan_histology.append(histo)
            scan_details["histology"] = scan_histology
        else:
            logger.warning("Unknown scan type for including in report")
            continue
        scan_videos = []
        appendix_videos = []
        scan_attachments = scan.scanattachment_set.filter(
            attachment_type__report_priority__gte=0).order_by("attachment_type__report_priority")
        logger.debug("Found %d attachments for inclusion", len(scan_attachments))
        type_xy_slice_roll = ScanAttachmentType.objects.get(name="XY Slice Roll")
        type_xz_slice_roll = ScanAttachmentType.objects.get(name="XZ Slice Roll")
        type_yz_slice_roll = ScanAttachmentType.objects.get(name="YZ Slice Roll")
        type_thick_slice_mip = ScanAttachmentType.objects.get(name="Thick Slice MIP")
        type_thick_slice_avg = ScanAttachmentType.objects.get(name="Thick Slice Avg")
        type_thick_slice_sum = ScanAttachmentType.objects.get(name="Thick Slice Sum")
        type_thick_slice_stdev = ScanAttachmentType.objects.get(name="Thick Slice StDev")
        type_3d_mip_spin = ScanAttachmentType.objects.get(name="3D MIP Spin")
        type_3d_vol_spin = ScanAttachmentType.objects.get(name="3D Volume Spin")
        type_xray_360_spin = ScanAttachmentType.objects.get(name="X-Ray 360 Spin")
        type_additional = ScanAttachmentType.objects.get(name="Additional Video")
        included_videos = []
        for attachment in scan_attachments:
            video_details = {}
            appendix = False
            if attachment.exclude_from_report:
                continue    #If it's been explicitly rejected just skip ita
            if attachment.attachment_type == type_xy_slice_roll:
                position = report.xy_slice_roll_position
            elif attachment.attachment_type == type_xz_slice_roll:
                position = report.xz_slice_roll_position
            elif attachment.attachment_type == type_yz_slice_roll:
                position = report.yz_slice_roll_position
            elif attachment.attachment_type == type_thick_slice_mip:
                position = report.thick_slice_mip_position
            elif attachment.attachment_type == type_thick_slice_avg:
                position = report.thick_slice_avg_position
            elif attachment.attachment_type == type_thick_slice_sum:
                position = report.thick_slice_sum_position
            elif attachment.attachment_type == type_3d_mip_spin:
                position = report.mip_3d_position
            elif attachment.attachment_type == type_3d_vol_spin:
                position = report.volume_3d_position
            elif attachment.attachment_type == type_xray_360_spin:
                position = report.xray_360_position
            elif attachment.attachment_type == type_additional:
                position = report.additional_videos_position
            elif attachment.attachment_type == type_thick_slice_stdev:
                position = report.thick_slice_stdev_position
            else:
                #It's not to be included in the report
                #This shouldn't be hit because they should also have negative priorities
                continue
            #Things common for all videos
            if position == SampleReport.APPENDIX:
                appendix = True
            elif position == SampleReport.EXCLUDED:
                continue # This type of attachment is excluded
            video_details["description"] = attachment.attachment_type.description
            if attachment.notes:
                video_details["notes"] = "<br/>".join(attachment.notes.split("\n"))
            video_details["url"] = attachment.url
            if video_details["url"]:
                #Thumbnail generation is expensive only do it if also have a URL
                try:
                    thumbnail = video2thumbnail(
                        Path(attachment.attachment.path), Path(temp_dir.name))
                    video_details["thumb"] = "file://{}".format(thumbnail)
                    if appendix:
                        appendix_videos.append(video_details)
                    else:
                        scan_videos.append(video_details)
                    included_videos.append(attachment.attachment_type.pk)
                    # Mark the type of video as included
                except Exception as err: #pylint: disable=broad-except
                    warnings.append("Unable to generate thumbnail for {}".format(str(attachment)))
                    logger.error("Unable to generate thumbnail for %d.", attachment.pk)
                    logger.warning(err)
            else:
                warnings.append("No URL stored for {}".format(str(attachment)))
                logger.warning("No URL stored for attachment %d", attachment.pk)
        scan_details["appendix_videos"] = appendix_videos
        scan_details["videos"] = scan_videos
        scan_details["images"] = scan_images
        logger.info("Included videos %s", str(included_videos))
        logger.info("Included images %s", str(scan_images))
        if (
                len(scan_videos) == 0 and
                not report.all_videos_excluded() and
                scan_type != "Histology Slide"):
            logger.error("No videos found for scan %s", scan_details["name"])
            errors.append("No videos found for scan {}".format(scan_details["name"]))
        type_position_mapping = [
            (type_xy_slice_roll, report.xy_slice_roll_position),
            (type_xz_slice_roll, report.xz_slice_roll_position),
            (type_yz_slice_roll, report.yz_slice_roll_position),
            (type_thick_slice_mip, report.thick_slice_mip_position),
            (type_thick_slice_avg, report.thick_slice_avg_position),
            (type_thick_slice_sum, report.thick_slice_sum_position),
            (type_3d_mip_spin, report.thick_slice_sum_position),
            (type_3d_vol_spin, report.volume_3d_position),
            (type_xray_360_spin, report.xray_360_position),
            (type_additional, report.additional_videos_position),
            (type_thick_slice_stdev, report.thick_slice_stdev_position)
        ]
        if scan_type != "Histology Slide":
            for (atype, position) in type_position_mapping:
                if(
                        position != SampleReport.EXCLUDED and
                        atype.pk not in included_videos):
                    msg = "No {} video found for scan {}".format(
                        atype.name, scan_details["name"])
                    logger.warning(msg)
                    warnings.append(msg)
        scans.append(scan_details)
    if report.further_analysis_text:
        further_analysis_text = report.further_analysis_text.split("\r")
    else:
        further_analysis_text = None
    context = {
        'xrh_id' : xrh_id,
        'project_title' : project_title,
        'original_id' : sample.original_id,
        'sample_description' : sample.description,
        'further_analysis' : further_analysis_text,
        "scans": scans,
        "delivered_pic_front" : delivered_pic_front,
        "delivered_pic_back" : delivered_pic_back,
        "returned_pic_front" : returned_pic_front,
        "returned_pic_back" : returned_pic_back,
        "generic_photos" : generic_photos,
        "generated" : generation_time.strftime("%Y-%m-%d  %T %Z"),
        "img_width" : IMG_WIDTH,
        "img_width_2" : IMG_WIDTH_2,
        "img_height" : IMG_HEIGHT,
        "overview_height" : OVERVIEW_HEIGHT,
        "status" : status,
        "storage_requirements" : storage_requirements,
        "extraction_method" : extraction_method,
        "species": sample.species,
        "tissue": sample.tissue,
        "condition":condition,
        "header_img" : str(HEADER_IMG),
    }
    logger.debug(context)
    html_string = render_to_string("samples/sample_report.html", context)
    html = HTML(string=html_string)
    output_file = Path(temp_dir.name, "{}_report.pdf".format(xrh_id))
    compressed_file = Path(temp_dir.name, "{}_report_com.pdf".format(xrh_id))
    html.write_pdf(target=str(output_file), presentational_hints=True)
    compress_pdf(output_file, compressed_file)
    if debug:
        html_file = Path(temp_dir.name, "report.html")
        with open(html_file, "w") as html_file:
            html_file.write(html_string)
        if errors:
            errors_file = Path(temp_dir.name, "errors.txt")
            with open(errors_file, "w") as error_file:
                error_file.write("\n".join(errors))
        if warnings:
            warnings_file = Path(temp_dir.name, "warnings.txt")
            with open(warnings_file, "w") as warnings_file:
                warnings_file.write("\n".join(warnings))
    else:
        if errors:
            report.generation_errors = "\n".join(errors)
            report.generation_success = False
        else:
            report.generation_success = True
            report.generation_errors = None
        if warnings:
            report.generation_warnings = "\n".join(warnings)
        else:
            report.generation_warnings = None
        report.date_generated = generation_time
        report.report.save(output_file.name, open(compressed_file, "rb"))
        report.save()
    return temp_dir

def generate_all_reports(force=False):
    """
        Iterate through the reports and generate any that need doing
        :param Boolean force: force regeneration of the report
    """
    logger = logging.getLogger("All report generator")
    logger.info("Acquiring lock")
    success = 0
    try:
        with Lock(LOCK_NAME, acquire_timeout=LOCK_TIMEOUT):
            logger.info("Got lock")
            if force:
                reports = SampleReport.objects.all()
            else:
                reports = SampleReport.objects.filter(date_generated__isnull=True)
            logger.debug("Reports to generate: %d", len(reports))
            for report in reports:
                try:
                    generate_report(report, force=force)
                    success += 1
                except Exception as exp: #pylint: disable=broad-except
                    logger.error(exp)
            return  (success, len(reports))
    except TimeoutError:
        logger.critical("Unable to get lock")
        return (0, -1)
