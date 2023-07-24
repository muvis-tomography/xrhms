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
DATASET_ONLINE = "ON"
DATASET_MISSING = "MI"
DATASET_ARCHIVED_DISK = "AD"
DATASET_ARCHIVED_MUVIS = "AM"
DATASET_MOVING = "MV"
DATASET_DELETED = "DE"

CAN_CHECK_STATUS_LIST = [
    DATASET_ONLINE,
    DATASET_MISSING,
    DATASET_DELETED,
]

DATASET_STATUS_CHOICES = [
    (DATASET_ONLINE, "Online"),
    (DATASET_MISSING, "Missing"),
    (DATASET_ARCHIVED_DISK, "Archived to Disk"),
    (DATASET_ARCHIVED_MUVIS, "Archived to Muvis"),
    (DATASET_MOVING, "Moving"),
    (DATASET_DELETED, "Deleted")
]
