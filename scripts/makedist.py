#!/usr/bin/python3
#
# Generate an addon release archive. For repeatability, the timestamp
# and contents for each file are taken from the last commit affecting
# that file.
#
# This script takes an arg identifying a specific commit (e.g. a tag)
# from which to generate the archive. For example, the command
#
#     ./make-dist v1.0
#
# will make an archive for the commit tagged “v1.0” (assuming it exists).
# This tag name will also be included in the created archive name.

import getopt
import os
import subprocess
import sys
import time
import zipfile
import pathlib

REPO_FILES = (
    "sources/",
)


def git(*args):
    # convenience routine for simplifying git command calls.
    return subprocess.check_output(("git",) + args)


opts, args = getopt.getopt(sys.argv[1:], "", [])
if len(args) != 1:
    raise getopt.GetoptError("expecting exactly one arg, the tag to build a release for")

upto = args[0]
earliest = git("rev-list", "--reverse", upto).split(b"\n")[0].strip().decode()

basename = "frame_avatar_addon"
outfilename = f"{basename}_{upto}.zip"
if pathlib.Path(outfilename).exists():
    os.remove(outfilename)
out = zipfile.ZipFile(outfilename, "x")
for item in REPO_FILES:
    if item.endswith("/"):
        items = sorted(
            set(
                line.rsplit("\t", 1)[1]
                for line in git("log", "--raw", item).decode().split("\n")
                if line.startswith(":")
            )
        )
    else:
        items = [item,]

    for filename in items:
        info = git("log", "--format=%ct:%H", "-n1", "%s..%s" % (earliest, upto), "--", filename).strip()

        if info != b"":
            info = zipfile.ZipInfo()
            info.filename = os.path.join(basename, filename[8:])
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            timestamp, commit_hash = info.split(b":")
            timestamp = int(timestamp)
            info = git("ls-tree", commit_hash, filename).strip()

        if info != b"":
            object_hash = info.split(b"\t")[0].split(b" ")[2].decode()
            object_contents = git("show", object_hash)
            info.date_time = time.gmtime(timestamp)[:6]
            out.writestr(info, object_contents)

out.close()

sys.stdout.write("created archive: %s\n" % outfilename)