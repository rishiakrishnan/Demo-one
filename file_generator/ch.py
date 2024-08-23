import yaml
from jinja2 import Environment, FileSystemLoader
import shutil

def copy_file(source, destination):
    try:
        shutil.copy(source, destination)
        print(f"File copied from {source} to {destination}")
    except Exception as e:
        print(f"Error copying file from {source} to {destination}: {e}")

# Example of copying a file
copy_file("pinmux/test/bsv_src/pinmux.bsv", "../sos/pinmux.bsv")