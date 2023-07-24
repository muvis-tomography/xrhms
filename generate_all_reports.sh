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

#Must be run from the correct directory

#open the virtual environment
source ../xrhms-env/bin/activate

#Load in the icinga submit code
source /opt/xrh-scripts/icinga_submit.sh
set -o pipefail
#update the database
output=`./generate_all_reports.py  2>>/opt/xrhms-venv/logs/reports.err | tee -a /opt/xrhms-venv/logs/reports.log`
update_status=$?
echo $output
icinga_submit $update_status "Report Generation" "$output"

#exit the virtualenv
deactivate

