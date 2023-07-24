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

./update_database.py -v /mnt/xrh-hot/CTData >> /opt/xrhms-venv/logs/ingest_hot.log 2>> /opt/xrhms-venv/logs/ingest_hot.err

update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "XRH Hot Ingest" "Ingest exited with code $update_status"
else
    icinga_submit $STATUS_OK "XRH Hot Ingest" "Ingest suceeded"
fi

./update_database.py -v /mnt/xrh-warm/CTData >> /opt/xrhms-venv/logs/ingest_warm.log 2>> /opt/xrhms-venv/logs/ingest_warm.err
update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "XRH Warm Ingest" "Ingest exited with code $update_status"
else
    icinga_submit $STATUS_OK "XRH Warm Ingest" "Ingest suceeded"
fi

./update_database.py -v /mnt/medx-data/CTData >> /opt/xrhms-venv/logs/ingest_medx-data.log 2>> /opt/xrhms-venv/logs/ingest_medx-data.err
update_status=$?
if [ $update_status -ne 0 ]; then
    icinga_submit $STATUS_CRITICAL "Med-X Data Ingest" "Ingest exited with code $update_status"
else
    icinga_submit $STATUS_OK "Med-X Data Ingest" "Ingest suceeded"
fi
#./update_database.py -v /mnt/medxdataB/External_academic/ >> /opt/xrhms-venv/logs/ingest_medx-ext-ac.log 2>> /opt/xrhms-venv/logs/ingest_medx-ext-ac.err
#update_status=$?
#if [ $update_status -ne 0 ]; then
#    icinga_submit $STATUS_CRITICAL "Med-X Ext-Ac Ingest" "Ingest exited with code $update_status"
#else
#    icinga_submit $STATUS_OK "Med-X Ext-Ac Ingest" "Ingest suceeded"
#fi
#exit the virtualenv
deactivate

