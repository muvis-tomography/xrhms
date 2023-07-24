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
from .archive_drive import ArchiveDrive, ScanArchive
from .attachment import ScanAttachment, ScanAttachmentType, ScanAttachmentTypeSuffix
from .gain import Gain
from .machine import Machine
from .nikon_scan import NikonCTScan
from .nikon_scan_modes import SCAN_MODE_CONTINUOUS, SCAN_MODE_STANDARD, SCAN_MODE_MRA, \
    SCAN_MODE_HELICAL
from .nikon_target_metals import TARGET_METAL_CHOICES
from .ome_channel import OmeChannel
from .ome_data import OmeData
from .ome_detector import OmeDetector
from .ome_image import OmeImage
from .ome_objective import OmeObjective
from .ome_plane import OmePlane
from .refined_raw import RefinedRawExtension, RefinedRawData
from .scan import Scan, generate_sidecar_filename, load_sidecar, SidecarStatus
from .scheduled_move import ScheduledMove
from .scanner_screenshot import ScannerScreenshot
from .server import Server
from .share import Share
from .staining import Staining
from .staining_attachment import StainingAttachment
from .user_copy import UserCopy
