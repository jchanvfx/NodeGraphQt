#!/usr/bin/env python
import os
import logging
import tempfile
from typing import Iterator


def get_base_dir() -> str:
    cur_path = os.path.dirname(__file__)
    base_path = os.path.realpath(os.path.join(cur_path, ".."))
    return base_path

def replace_in_file(fpath: str, old_str: str, new_str: str) -> None:
    _tfd, tpath = tempfile.mkstemp()
    with open(fpath, "r") as fd, os.fdopen(_tfd, "w") as tfd:
        for fline in fd:
            tline = fline.replace(old_str, new_str)
            tfd.write(tline)
    os.unlink(fpath)
    os.rename(tpath, fpath)

def get_source_files(root: str) -> Iterator[str]:
    cpath = os.path.realpath(__file__)
    for dname, dirs, files in os.walk(root):
        for fname in files:
            fpath = os.path.realpath(os.path.join(dname, fname))
            valid_file = fpath.endswith(".py")
            valid_file &= fpath != cpath
            if not valid_file:
                continue
            yield fpath


if __name__ == "__main__":
    base_dir = get_base_dir()
    for src_dir in ["examples", "NodeGraphQt"]:
        source_dir = os.path.join(base_dir, src_dir)
        for source_file in get_source_files(source_dir):
            logging.debug("Processing %s", source_file)
            replace_in_file(source_file, "from Qt", "from qtpy")
            replace_in_file(source_file, "import Qt,", "import qtpy,")
            replace_in_file(source_file, "import Qt\n", "import qtpy\n")
