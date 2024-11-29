#!/usr/bin/env python

"""Script converts Qt import to qtpy.

"""
import fnmatch
import os
import re
import sys

PYTHON_SCRIPT_PATH = sys.argv[1]

if os.path.isdir(PYTHON_SCRIPT_PATH):
    pattern = re.compile(r"^(from Qt) (.*)$")
    for root, dirs, files in os.walk(PYTHON_SCRIPT_PATH):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.py"):
                filepath = os.path.join(root, filename)
                filedata = []
                with open(filepath) as f:
                    for line in f.readlines():
                        match = pattern.match(line)
                        if match is not None:
                            line = f"from qtpy {match.group(2)}"
                        filedata.append(line.strip("\n"))
                with open(filepath, "w") as f:
                   f.write("\n".join(filedata))
else:
    print("Argument is not a directory")
