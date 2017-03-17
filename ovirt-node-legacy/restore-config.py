#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import subprocess
import sys


def uncompress(filename):
    exec_cmd(["tar", "zxvfp", filename, "--same-owner"])


def exec_cmd(cmd):
    process = subprocess.Popen(
        cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()


def extract_and_copy():
    print("Restoring..")
    for dir_name, subdir_list, file_list in os.walk("."):
        for fname in file_list:
            if "/config/" not in dir_name:
                continue
            src = "{0}/{1}".format(dir_name, fname)
            dest = "{0}/{1}".format(dir_name.replace("./config", ""), fname)
            print("{0}".format(dest))
            exec_cmd(["cp", "-p", src, dest])

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Argument requires: requires the /config"
              " from hypervisor in .tar.gz format!")
        sys.exit(0)

    uncompress(sys.argv[1])
    extract_and_copy()
