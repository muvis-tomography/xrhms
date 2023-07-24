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
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from user_profile.models import Profile
# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class WatchListInline(admin.TabularInline):
    model = get_user_model().watching.through
    verbose_name = "Watching project"
    verbose_name_plural = "Watching projects"
    max_rows = 0
    extra = 0

class UserAdmin(BaseUserAdmin):
    inlines = [
        ProfileInline,
        WatchListInline,
    ]

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
