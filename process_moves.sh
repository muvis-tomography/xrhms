#!/bin/bash
#   Copyright 2023 University of Southampton
#   Dr Philip Basford
#   μ-VIS X-Ray Imaging Centre
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#open the virtual environment
source ../xrhms-env/bin/activate

#Load in the icinga submit code
source /opt/xrh-scripts/icinga_submit.sh

./move_datasets.py -v -p  >> /opt/xrhms-venv/logs/move_datasets.log 2>> /opt/xrhms-venv/logs/move_datasets.err

update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "Dataset Move" "CRITICAL: Move failed with code $update_status"
else
    icinga_submit $STATUS_OK "Dataset Move" "OK: Processing dataset move queue suceeded"
fi
#exit the virtualenv
deactivate

