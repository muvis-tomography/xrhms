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

    Useful utility functions that will be helpful when processing datasets
"""
import sys
import re
import subprocess
import hashlib
from tempfile import TemporaryDirectory, NamedTemporaryFile
from pathlib import Path
from math import floor
from datetime import datetime, timezone
import logging
import os
import os.path
import zipfile
import numpy
import pyvips
import pyqrcode
from pylibdmtx.pylibdmtx import encode as dm_encode
import sh
import ffmpeg
import magic
from django.conf import settings

TYPES_TO_UPLOAD = [
    'video/x-msvideo',
    "video/mp4",
    "video/mpeg",
    "video/avi"
]

MINIMUM_OVERLAY_HEIGHT = 50

def calculate_file_hash(filename, buf_size=65536):
    """
        Calculate the sha256sum of a file
        based on https://stackoverflow.com/a/22058673/535237
        filename - file to hash
        buf_size (default 64kb)
    """
    sha = hashlib.sha256()
    with open(filename, "rb") as fhandle:
        while True:
            data = fhandle.read(buf_size)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

def tiff2png(filename, percent=100):
    """
        use pyvips to create a png from a tiff
        :param Path: filename - the tiff to convert
        :param int percent: Only save the bottom X percent of the pixel values
        :return (temp_dir, filename)
    """
    logger = logging.getLogger("tiff2png")
    logger.debug("Converting: %s", filename)
    temp_dir = TemporaryDirectory()
    logger.debug("Working dir: %s", temp_dir.name)
    image = pyvips.Image.new_from_file(str(filename))
    if  0 < percent < 100:
        logger.debug("Thresholding image")
        upper_limit = image.percent(percent)
        image = image * 255 / upper_limit

    new_filename = "{}.png".format(filename.stem)
    logger.debug("New filename: %s", new_filename)
    image.write_to_file(str(Path(temp_dir.name, new_filename)))
    return (temp_dir, new_filename)


def stack2xyslice(filename, pixels_x, pixels_y, pixels_z, bitdepth=None, position=0.5):
    """
        Go from a full stack to a single xy slice
        :param path filename: The full filename for the stack to process
        :param int pixels_x: Number of x pixels
        :param int pixels_y: Number of y pixels
        :param int pixels_z: total number of slices:
        :param int bitdepth: How many bits per pixel
        :param float position: value between 0 & 1 position in stack of slice
        :return (temp_dir, tiff_filename, png_filename)
    """
    logger = logging.getLogger("stack2xyslice")
    if position < 0:
        logger.error("Position (%f) cannot be less than 0.", position)
        raise ValueError("Position {:02f} cannot be less than 0.".format(position))
    if position > 1:
        logger.error("Position (%f) cannot be greater than 1.", position)
        raise ValueError("Position {:02f} cannot be greater than 1.".format(position))
    if bitdepth is None:
        vgi_file = vgi_from_vol(filename)
        bitdepth = read_vgi_bitdepth(vgi_file)
    logger.debug("Bitdepth = %d", bitdepth)
    if bitdepth == 8:
        dtype = numpy.uint8
        fmt = "uchar"
    elif bitdepth == 16:
        dtype = numpy.uint16
        fmt = "short"
    elif bitdepth == 32:
        dtype = numpy.float32
        fmt = "float"
    else:
        logger.error("Unsupported bitdepth %d", bitdepth)
        raise ValueError("Unsupported bitdepth {}".format(bitdepth))
    if not(isinstance(pixels_x, int) and isinstance(pixels_y, int) and isinstance(pixels_z, int)):
        logger.error("X %r Y %r Z %r must all be integers", pixels_x, pixels_y, pixels_z)
        logger.debug("X %r Y %r Z %r", type(pixels_x), type(pixels_y), type(pixels_z))
        raise ValueError("X, Y and Z must all be integers")
    logger.debug("Filename: %s", str(filename))
    bytes_per_pixel = bitdepth / 8
    logger.debug("Bytes per pixel: %d", bytes_per_pixel)
    pixels_per_slice = pixels_x * pixels_y
    logger.debug("Pixels per slice: %d", pixels_per_slice)
    bytes_per_slice = int(bytes_per_pixel * pixels_per_slice)
    logger.debug("Bytes per slice: %d", bytes_per_slice)
    logger.debug("position requested: %.2f", position)
    slices_into_stack = floor(position * pixels_z)
    logger.debug("Number of slices to skip: %d", slices_into_stack)
    bytes_to_skip = int(slices_into_stack * bytes_per_slice)
    logger.debug("Bytes to skip: %d", bytes_to_skip)
    filesize = file_size(filename)
    if filesize < (bytes_to_skip + bytes_per_slice):
        logger.warning("Don't have even reconstructed yet to get the middle slice")
        raise ValueError("volume not yet complete")
    data = numpy.fromfile(
        filename,
        dtype=dtype,
        count=bytes_per_slice,
        offset=bytes_to_skip)
    image = pyvips.Image.new_from_memory(data, pixels_x, pixels_y, 1, fmt)
    temp_dir = TemporaryDirectory()
    logger.debug("Working dir: %s", temp_dir.name)
    new_filename = "{}_xyslice".format(filename.stem)
    png_filename = "{}.png".format(new_filename)
    tif_filename = "{}.tif".format(new_filename)
    logger.debug("New filename: %s", new_filename)
    image.write_to_file(str(Path(temp_dir.name, png_filename)))
    image.cast("uchar").write_to_file(str(Path(temp_dir.name, tif_filename)))
    return (temp_dir, tif_filename, png_filename)

def generate_qr_code(url, fname="qr.png", scale=4):
    """
        Generate a QR for the specified URL:
        :param string url: The url to encode in the QR code
        :param string fname: The filename to write to
        :param int scale: How big to make the QR code
        :return (temp_dir, filename)
    """
    temp_dir = TemporaryDirectory()
    qr_code = pyqrcode.create(url)
    qr_code.png(str(Path(temp_dir.name, fname)), scale=scale)
    return (temp_dir, fname)

def generate_dm_code(url, fname="dm.png"):
    """
        Generate a dm200 code for the specified URL
        :param string url: The url to encode into the code
        :param string fname: The filename to write to
        :return (temp_dir, filename)
    """
    temp_dir = TemporaryDirectory()
    encoded = dm_encode(url.encode('utf-8'))
    image = pyvips.Image.new_from_memory(encoded.pixels, encoded.width, encoded.height, 3, "uchar")
    image.write_to_file(str(Path(temp_dir.name, fname)))
    return (temp_dir, fname)

def files_owned_by(path, user="root"):
    """
        Return a list of the files owned by the specified user
        :param Path path: The path to look in
        :param string user: The username to check for
        :return (count, list): The count and the a list of files that are owned by the user
    """
    logger = logging.getLogger("FilesOwnedBy")
    logger.debug("Looking for files owned by %s in %s", user, path)
    if not path.exists():
        logger.error("Path (%s) does not exist", path)
        raise ValueError("Path doesn't exist")
    cmd = "find {} -user {}".format(path, user)
    logger.debug("Using command: %s", cmd)
    output = subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if output.returncode != 0:
        logger.warning("The process encountered errors and may not be accurate")
    files_found = output.stdout.decode('utf-8').split("\n")
    while "" in files_found:
        files_found.remove("")
    logger.debug("Found %d files", len(files_found))
    return (len(files_found), files_found)

def directory_size(path):
    """
        Returns the size in bytes of the specified path in the filesystem
        :param Path path: The path to work out the size for
        :return int: size in bytes
    """
    if not path.exists():
        raise ValueError("The path must exist")
    return int(sh.du(path, "-sxb").split("\t")[0])

def file_size(path):
    """
        Returns the size in bytes of the file specified in the filesystem
        :param Path path: The path to work out the size for
        :return int: size in bytes
    """
    if not path.exists():
        raise ValueError("The path must exist")
    if not path.is_file():
        raise ValueError("The path must be a file")
    return path.stat().st_size

def count_files(path):
    """
        Returns the number of files found on the specified path"
        :param Path path: Where to look for files
        :return int: number of files
    """
    if not path.exists():
        raise ValueError("The path must exist")
    count = 0
    for dirpath, dirnames, files in os.walk(path): #pylint: disable=unused-variable
        count += len(files)
    return count

def free_space(mnt_point):
    """
        See how much space is available on a mount point
        :param Path mnt_point: The filesystem to check space on
        :return int: free space in bytes
    """
    if not mnt_point.exists():
        raise ValueError("Mount point must exist")
    return int(sh.df(mnt_point, "--output=avail", "--block-size=1").split("\n")[1])

def mount_size(mnt_point):
    """
        See how a mount point is (ie total size)
        :param Path mnt_point: The filesystem to check size of
        :return int: size in bytes
    """
    if not mnt_point.exists():
        raise ValueError("Mount point must exist")
    return int(sh.df(mnt_point, "--output=size", "--block-size=1").split("\n")[1])

def mount_free_percent(mnt_point):
    """
        What percentage of the mount point is free space
        :param Path mnt_point: The filesystem to check free space of
        :return float: percentage of free space
    """
    return free_space(mnt_point) / mount_size(mnt_point) * 100

def used_space(mnt_point):
    """
        See how much space is used on a mount point
        :param Path mnt_point: The filesystem to check usage on
        :return int : used space in bytes
    """
    if not mnt_point.exists():
        raise ValueError("Mount point must exist")
    return int(sh.df(mnt_point, "--output=used", "--block-size=1").split("\n")[1])

def list_xtekct_files(path):
    """
        Return a list of the xtekct files on the given path.
        :param Path path: Where to look for files
        :return List: of files
    """
    if not path.exists():
        raise ValueError("Path must exist")
    return list(path.glob("**/*.xtekct"))

def list_xtekhelixct_files(path):
    """
        Return a list of the xtekhelixct files on the given path.
        :param Path path: Where to look for files
        :return List: of files
    """
    if not path.exists():
        raise ValueError("Path must exist")
    return list(path.glob("**/*.xtekhelixct"))

def video2thumbnail(video, output_dir, position=0.5):

    """
        Take a video and use ffmpeg to generate a thumbnail of the specified time
        :param Path video: Path to the video to be processed
        :param Path output_dir: Path to the directory in which to save the thumbnail
        :param float position: 0 < position <=1 position through the stack to use for the thumbnail
        :return Path: Path to the thumbnail
    """
    logger = logging.getLogger("video2thumbnail")
    if position <= 0:
        raise ValueError("Position value ({}) too low.".format(position))
    if position > 1:
        raise ValueError("Position value ({}) too high.".format(position))
    (total_frames, frame_rate) = video_frame_count(video)
    logger.debug("Total frames: %d", total_frames)
    logger.debug("Frame rate: %f", frame_rate)
    target_frame = int(total_frames * position)
    logger.debug("Target frame: %d", target_frame)
    target_seconds = float(target_frame) / frame_rate
    logger.debug("Target seconds: %f", target_seconds)
    video_name = video.stem
    output_fname = Path(output_dir, "{}_thumbnail.png".format(video_name))
    (
        ffmpeg
        .input(str(video), ss=target_seconds)
        .output(str(output_fname), vframes=1)
        .global_args('-loglevel', 'error')
        .run()
    )
    return output_fname


def video_frame_count(video):
    """
        Work out how many frames a video has
        Based on https://github.com/kkroening/ffmpeg-python/blob/master/examples/video_info.py
        :param Path video: The video file to examine
        :return ( total_frames, frame_rate)
    """
    if not video.exists():
        raise FileNotFoundError("{} does not exist".format(str(video)))
    probe = ffmpeg.probe(str(video))
    video_stream = next(
        (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        raise ValueError("Unable to find video in file")
    total_frames = int(video_stream["nb_frames"])
    frame_rate_str = video_stream["r_frame_rate"]
    frame_rate_arr = frame_rate_str.split("/")
    frame_rate = float(frame_rate_arr[0]) / float(frame_rate_arr[1])
    return (total_frames, frame_rate)

def video_dimensions(video):
    """
        Work out the dimensions in pixels of a video stream
        Based on https://github.com/kkroening/ffmpeg-python/blob/master/examples/video_info.py
        :param Path video: The video file to examine
        :return (width, height)
    """
    if not video.exists():
        raise FileNotFoundError("{} does not exist".format(str(video)))
    probe = ffmpeg.probe(str(video))
    video_stream = next(
        (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        raise ValueError("Unable to find video in file")
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    return (width, height)

def image_dimensions(image):
    """
        Work out the dimensions in pixels of an image
        :param Path image: The image to analyse
        :return (width, height)
    """
    if not image.exists():
        raise FileNotFoundError("{} does not exist".format(str(image)))
    image_obj = pyvips.Image.new_from_file(str(image))
    return (image_obj.width, image_obj.height)

def apply_overlay(
        video, image, top=True, left=True,
        transparency=0.375, rel_height=0.1, margin=25, video_bitrate=5120000):
    """
        Overlay the specified image onto the video in the specified position
        :param Path video: The video to add the image to
        :param Path image: The image to add to the video
        :param boolean top: Default=True: Position at the top of the video
        :param boolean left: Default=True: Position at the left of the video
        :param float transparency: Default=0.375 How transparent to make the image
        :param float rel_height: Default=0.1 size of the overlay relative to the height of the video #pylint: disable=line-to-long
        :param int margin: Default=25 gap to between image and edge of frame
        :param int video_bitrate Bits per second to target the video encode at
        :return (temp_dir, filename)
    """
    logger = logging.getLogger("Video Overlay")
    if not video.exists():
        raise FileNotFoundError("{} does not exist".format(str(video)))
    if not image.exists():
        raise FileNotFoundError("{} does not exist".format(str(image)))
    if rel_height < 0 or rel_height > 1:
        raise ValueError("rel_height value ({}) must be betwen 0 and 1".format(rel_height))
    if transparency < 0 or transparency > 1:
        raise ValueError("tranparency value ({}) must be betwen 0 and 1".format(transparency))
    (video_width, video_height) = video_dimensions(video)
    logger.debug("Video dimensions %dx%d", video_width, video_height)
    frame_rate = video_frame_count(video)[1]
    logger.debug("Source frame rate %d", frame_rate)
    margin = int(margin)
    if margin < 0 or margin > video_width/2:
        raise ValueError("margin value ({}) must be an integer between 0 and {}".format(
            margin, int(video_width/2)))
    image_height = int(rel_height * video_height)
    if image_height < MINIMUM_OVERLAY_HEIGHT:
        logger.warning(
            "Overlay height (%d) below minimum (%d).  Overriding",
            image_height,
            MINIMUM_OVERLAY_HEIGHT)
        image_height = MINIMUM_OVERLAY_HEIGHT
    (orig_img_width, orig_img_height) = image_dimensions(image)
    image_aspect_ratio = orig_img_height / orig_img_width
    logger.debug("Image dimensions %dx%d (%f)", orig_img_width, orig_img_height, image_aspect_ratio)
    image_width = int(image_height / image_aspect_ratio)
    logger.debug("Scaled image dimensions %dx%d", image_width, image_height)
    if top:
        image_y_offset = margin
    else:
        image_y_offset = video_height - image_height - margin
    if left:
        image_x_offset = margin
    else:
        image_x_offset = video_width - image_width - margin
    logger.debug("Margin %d", margin)
    logger.debug("Image position %d,%d", image_x_offset, image_y_offset)
    logger.debug("Tranparency %f", transparency)
    image_obj = (
        ffmpeg
        .input(str(image))
        .filter("scale", image_width, image_height)
        .filter("format", "argb")
        .filter("geq", r="r(X,Y)", a="{}*alpha(X,Y)".format(transparency))
    )
    video_obj = ffmpeg.input(str(video))
    temp_dir = TemporaryDirectory()
    video_name = video.name
    output_path = Path(temp_dir.name, video_name)
    logger.debug("Output file %s", output_path)
    logger.debug("Using Bitrate: %d", video_bitrate)
    (
        ffmpeg
        .filter([video_obj, image_obj], "overlay", image_x_offset, image_y_offset)
        .output(str(output_path), framerate=frame_rate, video_bitrate=str(video_bitrate))
        .global_args('-loglevel', 'error')
        .run()
    )
    return (temp_dir, video_name)



def publically_uploadable_video_type(path):
    """
        Check to make sure that the file passed in is a video type that is appropriate
        to try to upload to something like YouTube
        :param Path path: The file to examine
    """
    if not path.exists():
        raise ValueError("File does not exist, cannot determine type")
    mime_type = magic.from_file(str(path), mime=True)
    return mime_type in TYPES_TO_UPLOAD

def dir_depth_sort_key(path):
    """
        Key to use to sort a list of directories by depth.
        This is handy because du will ignore directories if it has already counted them
        :param Path path: The path to work out the rank for
    """
    return len(path.parts)

def convert_filesize(num, suffix="B"):
    """
        Based on https://stackoverflow.com/a/1094933
        Convert a number of bytes into a human readable string
        :param float/int num: The number to be converted
        :param char suffix: The suffix to use
        :return string: human readable filesize
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def compress_pdf(fname_in, fname_out):
    """
        Use ghostscript to compress the PDF
        :param Path fname_in: The file to convert
        :param Path fname_out: The file to write to
    """
    if not fname_in.exists():
        raise FileNotFoundError("{} does not exist".format(fname_in))
    if fname_out.exists():
        raise ValueError("{} already exists".format(fname_out))
    cmd = (
        "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dNOPAUSE "
        + "-dQUIET -dBATCH -dPrinted=false -sOutputFile={} {}".format(fname_out, fname_in))
    output = subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if output.returncode != 0:
        raise IOError("Unable to compress PDF")


def create_report_bundle(queryset):
    """
        Create a zip file containing the reports listed in the queryset
        :return NamedTemporaryFile: The file containing the zip file
    """
    temp_file = NamedTemporaryFile()
    bundle = zipfile.ZipFile(temp_file, "w", zipfile.ZIP_DEFLATED)
    for report in queryset:
        path = Path(report.report.path)
        name = path.name
        bundle.write(path, name)
    bundle.close()
    return temp_file

def validate_user(username):
    """
        Check the specified username exists and is known about by the system)
        :return Boolean: True if the username exists
    """
    return len(sh.finger(username)) != 0

def find_mount_point(path):
    """
        Find the mountpoint for the specified path
        https://stackoverflow.com/a/4453715/535237
        :param Path path
        :return Path
    """
    if not isinstance(path, Path):
        raise ValueError("Must be a path")
    if os.path.ismount(path):
        return path
    return find_mount_point(path.parent)

def get_file_modified_time(path):
    """
        Get the modified time of the file
        :param Path path: The file to get the modified time for
        :return datetime
    """
    if not isinstance(path, Path):
        raise ValueError("Must be a path")
    if not path.exists():
        raise ValueError("File must exist")
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

def strip_ansi_codes(string):
    """
        Remove ascii colour codes from a string
        https://stackoverflow.com/a/15780675/535237
        :param String input
        :return String output
    """
    return re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', string)

def read_vgi_bitdepth(vgi_file):
    """
        Reads a vgi file and returns the specified bit depth
        :param Path vgi_file: The path to the vgi file to read
        :return int bitdepth
    """
    if not isinstance(vgi_file, Path):
        raise ValueError("Must be a path")
    if not vgi_file.exists():
        raise ValueError("File must exist")
    for line in open(vgi_file).readlines():
        if line.startswith("bitsperelement"):
            arr = line.split("=")
            return int(arr[1])

def vgi_from_vol(vol_file):
    """
        Work out the vgi filename for the specified vol file
        :param Path vol_file: The volume file to work out the associated vgi file for
        :return Path vgi file
    """
    return Path(vol_file.parent, "{}.vgi".format(vol_file.stem))

def find_eaDir(path): #pylint: disable=invalid-name
    """
        Search the specified path for any eaDir folders.
        These folders are created by the synologies and can cause grief when moving datasets
        :param Path path: Where to search
        :return array folders
    """
    cmd = f"find \"{path}\" -name \"@eaDir\""
    out = subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    arr = out.stdout.decode(sys.stdout.encoding).strip().split("\n")
    return [x for x in arr if x]

def count_eaDir(path): #pylint: disable=invalid-name
    """
        Count the number of eaDirs in the path specified
        :param Path: where to count the folders
        :return int number found
    """
    return len(find_eaDir(path))

def delete_eaDir(path): #pylint: disable=invalid-name
    """
        Delete all instance of eaDir in the path given
        :param Path path where to look for eaDir folders
    """
    cmd_path = Path(settings.BASE_DIR, "remove_eaDir.sh")
    cmd = f"sudo {cmd_path} \"{path}\""
    print(cmd)
    output = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    print(f"Command status {output.returncode}")
