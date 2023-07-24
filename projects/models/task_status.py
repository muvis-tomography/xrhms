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

    Possible options for an update next_action_status
"""
TASK_COMPLETE = "CO"
TASK_PENDING = "PE"
TASK_WONT_DO = "WD"

TASK_STATUS_CHOICES = [
    (TASK_COMPLETE, "Complete"),
    (TASK_PENDING, "Pending"),
    (TASK_WONT_DO, "Won't Complete"),
]
