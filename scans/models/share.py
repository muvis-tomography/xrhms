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

    Represents shares for data storage
"""
from django.db import models

from .dataset_status import DATASET_STATUS_CHOICES

class Share(models.Model):
    name = models.CharField(
        max_length=30,
        db_index=True,
        unique=True,
        help_text="The name of the share")
    server = models.ForeignKey(
        "Server",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text="The server the share is stored on")
    linux_mnt_point = models.CharField(
        max_length=100,
        db_index=True,
        unique=True,
        blank=True,
        null=True,
        verbose_name = "Linux mount point",
        help_text="The path to access the share when mounted under linux")
    windows_mnt_point = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name = "Windows mount point",
        help_text="The path to access the share when mounted under windows")
    default_status = models.CharField(
        max_length=2,
        choices=DATASET_STATUS_CHOICES,
        blank=False,
        null=False,
        help_text="The default status of a dataset on this share")
    generate_extra_folder = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Collate other information into the extra folder when moving here")


    def internal_mnt_path(self):
        if self.server.internal_name is None: #pylint:disable=no-member
            return "-"
        return "//{}/{}".format(self.server.internal_name, self.name).replace("/", "\\")  #pylint:disable=no-member
    internal_mnt_path.short_description = "Internal mount path"

    def internal_ipv4_mnt_path(self):
        if self.server.internal_ipv4_address is None: #pylint:disable=no-member
            return "-"
        return "//{}/{}".format(self.server.internal_ipv4_address, self.name).replace("/", "\\") #pylint:disable=no-member
    internal_ipv4_mnt_path.short_description = "Internal IPv4 mount path"

    def internal_ipv6_mnt_path(self):
        if self.server.internal_ipv6_address is None: #pylint:disable=no-member
            return "-"
        return "//{}/{}".format(self.server.internal_ipv6_address, self.name).replace("/", "\\")  #pylint:disable=no-member
    internal_ipv6_mnt_path.short_description = "External IPv6 mount path"

    def external_mnt_path(self):
        if self.server.external_name is None: #pylint:disable=no-member
            return "-"
        return "//{}/{}".format(self.server.external_name, self.name).replace("/", "\\")  #pylint:disable=no-member
    external_mnt_path.short_description = "External mount path"

    def external_ipv4_mnt_path(self):
        if self.server.external_ipv4_address is None: #pylint:disable=no-member
            return "-"
        return "//{}/{}".format(self.server.external_ipv4_address, self.name).replace("/", "\\") #pylint:disable=no-member
    external_ipv4_mnt_path.short_description = "External IPv4 mount path"

    def external_ipv6_mnt_path(self):
        if self.server.external_ipv6_address is None: #pylint:disable=no-member
            return "-"
        return "////{}/{}".format(self.server.external_ipv6_address, self.name).replace("/", "\\")  #pylint:disable=no-member
    external_ipv6_mnt_path.short_description = "External IPv4 mount path"


    def __str__(self):
        return "{}/{}".format(self.server.host_name, self.name) #pylint:disable=no-member
