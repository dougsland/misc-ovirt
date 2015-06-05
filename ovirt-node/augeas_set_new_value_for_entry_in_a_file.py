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

# Example of setting new value for driftfile in /etc/ntp.conf
aug = utils.AugeasWrapper()
ntp_conf_drift = "/files/etc/ntp.conf/driftfile"

if aug.match(ntp_conf_drift):
    print("Current value of drift %s" % aug.get(ntp_conf_drift))
    aug.set(ntp_conf_drift, "/lib/ntp/drift")
    print("New value of driftfile %s" % aug.get(ntp_conf_drift))
