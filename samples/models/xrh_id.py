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


    Methods to handle the XRH ID validation and splitting into different fields.
    XRH ID takes the form XXXXNNNNC-SSSS
    XXXX = Alphabetic (capitals) prefix for grouping samples
    NNNN = ID number of the sample (4 digit minimum may be more)
    C = Check digita for the numerical part
    SSSS = OPTIONAL sequence ID for when a sample has been sectioned into slices

    Based on work from the previous pathfinder project.

"""

#The lookup table to use to calculate the check digit
#https://en.wikipedia.org/wiki/Damm_algorithm
#http://archiv.ub.uni-marburg.de/diss/z2004/0516/pdf/dhmd.pdf
_TABLE = [
    [0, 3, 1, 7, 5, 9, 8, 6, 4, 2],
    [7, 0, 9, 2, 1, 5, 4, 8, 6, 3],
    [4, 2, 0, 6, 8, 7, 1, 3, 5, 9],
    [1, 7, 5, 0, 9, 8, 3, 4, 2, 6],
    [6, 1, 2, 3, 0, 4, 5, 9, 7, 8],
    [3, 6, 7, 4, 2, 0, 9, 5, 8, 1],
    [5, 8, 6, 9, 7, 2, 0, 1, 3, 4],
    [8, 9, 4, 5, 3, 6, 2, 0, 1, 7],
    [9, 4, 3, 8, 6, 1, 7, 2, 0, 5],
    [2, 5, 8, 1, 4, 3, 6, 7, 9, 0]
]


def get_numeric(id_str, check_digit=True):
    """
        Get just the numerical part of the ID string
        check_digit: include the check digit in the response
    """
    id_num = int(split(id_str)[1])
    if check_digit:
        return id_num
    return int(id_num/10)

def get_prefix(id_str):
    """
        Get just the prefix of the ID string
    """
    return split(id_str)[0]

def get_suffix(id_str):
    """
        Get just the suffix of the ID string (may be None)
    """
    return split(id_str)[2]

def split(id_str):
    """
        Split the string into the component parts of the ID
        returns an array containing the different parts of the ID string
        0 = prfix
        1 = numeric part
        2 = suffix (may be None )
    """
    if "-" in id_str:
        #It has a suffix
        arr = id_str.split("-")
        suffix = _validate_suffix(arr[1])
        prefix = _validate_prefix(arr[0][0:4])
        number = _validate_number(arr[0][4:])
    else:
        prefix = _validate_prefix(id_str[0:4])
        number = _validate_number(id_str[4:])
        suffix = None
    return [prefix, number, suffix]

def _validate_prefix(prefix):
    """
        Check that the prefix meets the required constraints
    """
    if not str(prefix).isalpha():
        raise XrhIdValidationError(
            "Prefix ({}) must contain alpabetical characters only".format(prefix))
    return prefix.upper() # make sure it's upper case

def _validate_number(number):
    """
        Check that the numeric part meets the required constraints
    """
    if not str(number).isnumeric():
        raise XrhIdValidationError("Sample number ({}) must be a number".format(number))
    return number

def _validate_suffix(suffix):
    """
        Check that the suffix meets the required constraints
    """
    if suffix is None:
        return None
    if not str(suffix).isalnum():
        raise XrhIdValidationError("Suffix ({}) must be alphanumeric".format(suffix))
    return suffix.upper()

def generate(prefix, number, suffix=None):
    """
        Take the 3 component parts and combine into a single string representation
        prefix = the alphabetic part
        number = the numeric part (EXCLUDING check digit)
        suffix = OPTIONAL
    """
    prefix = _validate_prefix(prefix)
    number = _validate_number(number)
    check_digit = calculate(number)
    output = "{}{:04d}{}".format(prefix, int(number), check_digit)
    if suffix is not None:
        suffix = _validate_suffix(suffix)
        output += "-{}".format(suffix)
    return output


def check_digit_ok(id_str):
    """
        Checks to make sure that the id_str check digit is ok
        Only checks the middle numerical part
    """
    id_str = str(id_str) #make sure it's a string
    if not id_str.isnumeric():
        number = get_numeric(id_str)
    else:
        number = id_str
    check_digit = calculate(number)
    if check_digit != 0:
        raise  XrhIdValidationError("Invalid ID number {}.".format(id_str))
    return True


def calculate(number, start_digit=0):
    """
        Calculate what the check digit should be
        start_digit = the primer for the algorithm
    """
    digit = start_digit
    for c in str(number): #pylint:disable=invalid-name
        digit = _TABLE[digit][int(c)]
    return digit


class XrhIdValidationError(Exception):
    """
        Error to be thrown when the passed in number does not validate
    """
