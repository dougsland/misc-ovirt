#!/usr/bin/python
#
# Copyright (C) 2015
#
# Douglas Schilling Landgraf <dougsland@redhat.com>
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301
# USA

from ovirt.node import utils

# Example of removing server entries from /etc/ntp.conf
aug = utils.AugeasWrapper()
ntp_conf_server = "/files/etc/ntp.conf/server"

if aug.match(ntp_conf_server):
    print("Removing all server entries in /etc/ntp.conf")
    aug.remove(ntp_conf_server)
