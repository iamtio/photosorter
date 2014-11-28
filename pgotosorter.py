from __future__ import print_function, unicode_literals, division
import os
import glob
import sys
import argparse
from datetime import datetime
from PIL import Image

def get_file_date(input_file):
    """Get file creation date"""
    try:
        with open(input_file, 'rb') as file:
            date = str(Image.open(file)._getexif()[36867]) # DateTimeOriginal
        date = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
    except KeyError:
        msg = "Warning! EXIF tag not found"\
              "for file '{0}'".format(input_file)
        print(msg, file=sys.stderr)
        date = datetime.fromtimestamp(os.path.getctime(input_file))
    return date


def find_files(directory, filter, recursive):
    """Filter files in directory"""
    dirs = [directory]
    if recursive:
        dirs = (d[0] for d in os.walk(directory))
    for dir in dirs:
        for file in glob.iglob(os.path.join(dir.decode('utf-8'), filter)):
            yield file


def safe_file(file, directory):
    """Generate safe file path into new directory"""
    new_file = None
    exist = 0
    while True:
        safe_name = os.path.split(file)[-1]
        if exist > 0:
            parts = safe_name.split(".")
            safe_name = "{0}({1}).{2}".format(".".join(parts[:-1]),
                                              exist, parts[-1])
        new_file = os.path.join(directory,
                                safe_name)
        if os.path.isfile(new_file):
            exist += 1
        else:
            break
    return new_file


def move_file(file, date, directory):
    """Move file to structured by date directory"""
    df = date.strftime
    new_directory = \
        os.path.join(directory, df("%Y"), df("%Y_%m"), df("%Y_%m_%d"))

    print("Moving to {0} from {1}".format(
        os.path.abspath(safe_file(file, new_directory)),
        os.path.abspath(file)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d',
                        metavar="DIR",
                        help="Directory to scan files",
                        required=True)
    parser.add_argument('--recursive', '-r',
                        help="Find files in subdirs",
                        action="store_true")
    parser.add_argument('--filter', '-f',
                        metavar="GLOB",
                        help="Filter files. Default: '*.jpg'",
                        default="*.jpg")
    args = vars(parser.parse_args())
    for file_name in find_files(**args):
        date = get_file_date(file_name)
        move_file(file_name, date, args['directory'])