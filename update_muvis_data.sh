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
SCRIPT=/opt/xrhms-venv/xrhms/update_muvis_data.py


#Load in the icinga submit code
source /opt/xrh-scripts/icinga_submit.sh

#update the database
$SCRIPT http://muvis.soton.ac.uk/cgi-bin/ctscans.json -q
update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "Muvis Update (academic)" "Update exited with code $update_status"
else
    icinga_submit $STATUS_OK  "Muvis Update (academic)" "OK: Update success"
fi


$SCRIPT http://muvis.soton.ac.uk/cgi-bin/ctscans_com.json -q
update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "Muvis Updatei (commercial)" "Update exited with code $update_status"
else
    icinga_submit $STATUS_OK "Muvis Update (commercial)" "OK: Update success"
fi

$SCRIPT http://muvis.soton.ac.uk/cgi-bin/ctscans_maintenance.json -q
update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "Muvis Update (maintenance) " "Update exited with code $update_status"
else
    icinga_submit $STATUS_OK "Muvis Update (maintenance)" "OK: Update success"
fi
