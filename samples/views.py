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
import csv
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
# Create your views here.


def sample_details_csv(samples):
    response = HttpResponse(content_type="text\\csv")
    response['Content-Disposition'] = 'attachment; filename="samples.csv"'
    csv_writer = csv.writer(response)
    csv_writer.writerow([
        "XRH ID", "Original ID", "Projects", "Species", "Tissue",
        "Sample type", "Current status/location"])
    for sample in samples:
        full_xrh_id = sample.full_xrh_id
        original_id = sample.original_id
        project_names = []
        for project in sample.project.all():
            project_names.append(project.name)
        project_list = "'{}'".format("','".join(project_names))
        species = str(sample.species)
        tissue = str(sample.tissue)
        sample_type = str(sample.sample_type)
        try:
            current_status = str(sample.current_location())
        except ObjectDoesNotExist:
            current_status = "Unknown"
        csv_writer.writerow([
            full_xrh_id,
            original_id,
            project_list,
            species,
            tissue,
            sample_type,
            current_status
        ])
    return response
