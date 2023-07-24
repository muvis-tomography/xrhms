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

    xrhms URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
    Examples:
    Function views
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    Class-based views
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, reverse
from django.shortcuts import redirect

from django.conf import settings

import private_storage.urls

admin.site.site_header = "XRH Management System"
if settings.DEV_SITE:
    admin.site.site_header += " DEVELOPMENT VERSION"
admin.site.site_title = "XRH Management Admin Portal"
admin.site.index_title = "Welcome to XRH Management system"
admin.site.site_url = None
def redirect_index(request):
    """
        Redirect the front page to the admin page login
    """
    return redirect(reverse("admin:index"))

def redirect_nikonctscanattachment(request, pk=None):
    if pk:
        return redirect("/admin/scans/scanattachment/{}/change".format(pk))
    return redirect("/admin/scans/scanattachment")

urlpatterns = [
    path('admin/scans/nikonctscanattachment/', redirect_nikonctscanattachment),
    path('admin/scans/nikonctscanattachment/<int:pk>/change/', redirect_nikonctscanattachment),
    path('admin/', admin.site.urls),
    path('', redirect_index),
    path('private-media/', include(private_storage.urls)),
]
