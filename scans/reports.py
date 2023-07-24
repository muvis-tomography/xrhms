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

    Generate a report for the scan for all projects that exist for the sample
"""

import logging

from samples.models import SampleReport, ReportScanMapping

def generate_basic_report_tasks(scan, log_level=logging.WARNING):
    logger = logging.getLogger("Scan basic report generator")
    logger.setLevel(log_level)
    logger.debug("Generating basic report for scan %d", scan.pk)
    sample = scan.sample
    if not sample:
        logger.error("No sample set for scan unable to generate report")
        raise ValueError("No sample set for scan unable to proceed")
    projects = sample.project.all()
    if len(projects) == 0:
        logger.error("No projects on sample, unable to generate report")
        raise ValueError("No project set on sample, unable to proceed")
    logger.debug("Generating reports for %d projects", len(projects))
    for project in projects:
        logger.debug("Project: %s", project)
        report = SampleReport()
        report.sample = sample
        report.project = project
        report.yz_slice_roll_position = SampleReport.EXCLUDED
        report.xz_slice_roll_position = SampleReport.EXCLUDED
        report.xy_slice_roll_position = SampleReport.EXCLUDED
        report.thick_slice_mip_position = SampleReport.EXCLUDED
        report.thick_slice_avg_position = SampleReport.EXCLUDED
        report.thick_slice_sum_position = SampleReport.EXCLUDED
        report.mip_3d_position = SampleReport.EXCLUDED
        report.volume_3d_position = SampleReport.EXCLUDED
        report.xray_360_position = SampleReport.EXCLUDED
        report.additional_videos_position = SampleReport.EXCLUDED
        report.thick_slice_stdev_position = SampleReport.EXCLUDED
        report.returned_photos = False
        report.generic_photos = False
        report.projections = True
        report.xy_slice = True
        report.save()
        rsm = ReportScanMapping()
        rsm.report = report
        rsm.scan = scan
        rsm.save()
