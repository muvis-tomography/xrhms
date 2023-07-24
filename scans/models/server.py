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

    Represents servers used to store the data
"""
from django.db import models

class Server(models.Model):
    host_name = models.CharField(
        max_length=30,
        db_index=True,
        unique=True,
        help_text="The name of the server")
    internal_name = models.CharField(
        max_length=100,
        db_index=True,
        unique=True,
        blank=True,
        null=True,
        help_text="The internal hostname of the server")
    internal_ipv4_address = models.GenericIPAddressField(
        protocol="ipv4",
        blank=True,
        null=True,
        verbose_name="Internal IPv4 address",
        help_text="The internal IPv4 address of the server")
    internal_ipv6_address = models.GenericIPAddressField(
        protocol="ipv6",
        blank=True,
        null=True,
        verbose_name="Internal IPv6 address",
        help_text="The internal IPv6 address of the server")
    external_name = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        help_text="The external hostname of the server")
    external_ipv4_address = models.GenericIPAddressField(
        protocol="ipv4",
        blank=True,
        null=True,
        verbose_name="external IPv4 address",
        help_text="The external IPv4 address of the server")
    external_ipv6_address = models.GenericIPAddressField(
        protocol="ipv6",
        blank=True,
        null=True,
        verbose_name="external IPv6 address",
        help_text="The external IPv6 address of the server")

    def __str__(self):
        return self.host_name
