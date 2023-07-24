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

    Views for producing labels for printing
"""

from tempfile import TemporaryDirectory
import logging
from pathlib import Path
from django.utils.html import mark_safe
from django.template.loader import render_to_string
from weasyprint import HTML

from xrhms.settings import BASE_DIR
# Create your views here.

LABEL_11354_WIDTH_MM = 57
LABEL_11354_HEIGHT_MM = 32

LABEL_30321_WIDTH_MM = 88
LABEL_30221_HEIGHT_MM = 35

def sample_label(
        sample, version=1, width=LABEL_11354_WIDTH_MM,
        height=LABEL_11354_HEIGHT_MM, debug=False):
    """
        Generate a PDF for a label for a sample
        :param Sample sample: The record for which to produce a label
        :param int version: Style of label to print. Valid options [1]
        :param int width: x dimension of printed label
        :param int height: y dimension of printed label
        :param Boolean debug: Store html output in folder?
        :return (temp_dir, filename) if successful
    """
    logger = logging.getLogger("Sample Label")
    available_versions = [1]
    if version not in available_versions:
        logger.error("Unknown version (%d), available versions %r", version, available_versions)
        return None
    if not sample:
        logger.error("No sample passed in")
        return None
    qr_code_path = sample.qr_code.path
    qr_code = None
    if not qr_code_path:
        logger.warning("No QR code found")
    qr_code = "file://{}".format(qr_code_path)
    if sample.storage_requirement:
        storage_requirement = sample.storage_requirement.name
    else:
        storage_requirement = None
    additional_risks =  sample.sample_type.additional_risks
    warning_image = Path(BASE_DIR, "labels/templates/labels/warning-sign.png")
    if version == 1:
        template_name = "sample_label_v1.html"
        context = {
            'xrh_id' : sample.xrh_id(),
            'original_id' : sample.original_id,
            'qr_code' : qr_code,
            'storage_requirement' : storage_requirement,
            'additional_risks' : additional_risks,
            'warning_image' : "file://" + str(warning_image),
        }
    context['width'] = width
    context['height'] = height
    logger.debug(context)
    template_path = "labels/{}".format(template_name)
    logger.debug("Using template: %s", template_name)
    html_string = render_to_string(template_path, context)
    html = HTML(string=html_string)
    temp_dir = TemporaryDirectory()
    label_file = "label.pdf"
    output_file = Path(temp_dir.name, label_file)
    html.write_pdf(target=str(output_file), presentational_hints=True)
    if debug:
        html_file_name = Path(temp_dir.name, "label.html")
        with open(html_file_name, "w") as html_file:
            html_file.write(html_string)
    return (temp_dir, label_file)

def archive_drive_label(
        drive, version=1, width=LABEL_11354_WIDTH_MM,
        height=LABEL_11354_HEIGHT_MM, debug=False):
    """
        Generate a PDF label for an archive drive
        :param ArchiveDrive drive: The drive to label
        :param int height: y dimension of printed label
        :param Boolean debug: Store html output in folder?
        :return (temp_dir, filename) if successful
    """
    logger = logging.getLogger("Drive labelling")
    available_versions = [1]
    if version not in available_versions:
        logger.error("Unknown version (%d), available versions %r", version, available_versions)
        raise ValueError("Unknown version {}".format(version))
    if not drive:
        logger.error("Must specify a drive")
        raise ValueError("No drive specified")
    qr_code_path = drive.qr_code.path
    qr_code = "file://{}".format(qr_code_path)
    if version == 1:
        template_name = "archive_drive_label_v1.html"
        context = {
            'drive_id' : drive.pk,
            'qr_code' : qr_code,
            'created' : drive.date_created,
        }
    context['width'] = width
    context['height'] = height
    logger.debug(context)
    template_path = "labels/{}".format(template_name)
    logger.debug("Using template: %s", template_name)
    html_string = render_to_string(template_path, context)
    html = HTML(string=html_string)
    temp_dir = TemporaryDirectory()
    label_file = "label.pdf"
    output_file = Path(temp_dir.name, label_file)
    html.write_pdf(target=str(output_file), presentational_hints=True)
    if debug:
        html_file_name = Path(temp_dir.name, "label.html")
        with open(html_file_name, "w") as html_file:
            html_file.write(html_string)
    return (temp_dir, label_file)


def project_label(
        project, version=1, width=LABEL_11354_WIDTH_MM,
        height=LABEL_11354_HEIGHT_MM, debug=False):
    """
        Generate a PDF for a label for a sample
        :param Project project: The record for which to produce a label
        :param int version: Style of label to print. Valid options [1]
        :param int width: x dimension of printed label
        :param int height: y dimension of printed label
        :param Boolean debug: Store html output in folder?
        :return (temp_dir, filename) if successful
    """
    logger = logging.getLogger("Project Label")
    available_versions = [1]
    if version not in available_versions:
        logger.error("Unknown version (%d), available versions %r", version, available_versions)
        raise ValueError("Uknown version {}".format(version))
    if not project:
        logger.error("No project passed in")
        raise ValueError("No project passed in")
    qr_code_path = project.qr_code.path
    qr_code = None
    if not qr_code_path:
        logger.warning("No QR code found")
    qr_code = "file://{}".format(qr_code_path)
    if version == 1:
        template_name = "project_label_v1.html"
        context = {
            'project_id' : project.pk,
            'qr_code' : qr_code,
            'title': project.name,
            "pi": project.pi
        }
    context['width'] = width
    context['height'] = height
    logger.debug(context)
    template_path = "labels/{}".format(template_name)
    logger.debug("Using template: %s", template_name)
    html_string = render_to_string(template_path, context)
    html = HTML(string=html_string)
    temp_dir = TemporaryDirectory()
    label_file = "label.pdf"
    output_file = Path(temp_dir.name, label_file)
    html.write_pdf(target=str(output_file), presentational_hints=True)
    if debug:
        html_file_name = Path(temp_dir.name, "label.html")
        with open(html_file_name, "w") as html_file:
            html_file.write(html_string)
    return (temp_dir, label_file)

def address_label(
        contact, version=1, width=LABEL_30321_WIDTH_MM,
        height=LABEL_30221_HEIGHT_MM, debug=False):
    logger = logging.getLogger("Address Label")
    available_versions = [1]
    if version not in available_versions:
        logger.error("Unknown version (%d), available versions %r", version, available_versions)
        raise ValueError("Uknown version {}".format(version))
    if not contact:
        logger.error("No contact passed in")
        raise ValueError("No contact passed in")
    if not contact.address:
        logger.error("Contact doesn't have an address")
        raise ValueError("Contact doesn't have an address")
    if version == 1:
        template_name = "address_label_v1.html"
        context = {
            'name': contact.name,
            'address': mark_safe(contact.address.replace("\n", "<br/>"))
        }
        if contact.affiliation.count() == 1:
            context['affiliation'] = contact.affiliation.get()
        else:
            context['affiliation'] = None
            logger.info("Either none or multiple affiliations, ignoring")
    context["width"] = width
    context['height'] = height
    logger.debug(context)
    template_path = "labels/{}".format(template_name)
    logger.debug("Using template: %s", template_name)
    html_string = render_to_string(template_path, context)
    html = HTML(string=html_string)
    temp_dir = TemporaryDirectory()
    label_file = "label.pdf"
    output_file = Path(temp_dir.name, label_file)
    html.write_pdf(target=str(output_file), presentational_hints=True)
    if debug:
        html_file_name = Path(temp_dir.name, "label.html")
        with open(html_file_name, "w") as html_file:
            html_file.write(html_string)
    return (temp_dir, label_file)
