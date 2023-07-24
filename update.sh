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


#Update the currently deployed site

#Get the latest code from the repo
git pull
if [ $? -ne 0 ]
then
    echo "Git pull failed, ABORTING"
    exit 1
fi
#open the virtual environment
source ../xrhms-env/bin/activate
#apply the database updates needed
./manage.py migrate
#collect all the static content into the required folder
./manage.py collectstatic
sudo chgrp www-data -R static
sudo chmod g+r -R static/
sudo chmod g+X -R static/

#trigger a reload of the site
touch xrhms/wsgi.py
#exit the virtualenv
deactivate
