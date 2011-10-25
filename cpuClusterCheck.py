#!/usr/bin/python
#
# Copyright (C) 2011
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

import sys
import string

def checkCPUIntel():

	RHEV3_SUPPORTED = False
	cpu_family = ""
	model = "0"

	fd = open("/proc/cpuinfo", "r")
	for line in fd.readlines():
		if "cpu family\t" in line:
			value = line.split(':')
			cpu_family = value[1].strip('\n').strip(' ')
		
		if "model\t\t" in line:
			value = line.split(':')
			model = value[1].strip('\n').strip(' ')

			if cpu_family == "6":
				if model == "26" or model == "30" or model == "31" or model == "46":
					print "Arch: Nehalem\n"
					RHEV3_SUPPORTED = True

				if model == "23" or model == "29":
					print "Arch: Penryn"
					RHEV3_SUPPORTED = True

				if model == "22":
					print "Arch: Conroe"
					RHEV3_SUPPORTED = True

				if model == "37" or model == "44" or model == "47":
					print "Arch: Westmere"
					RHEV3_SUPPORTED = True

			if RHEV3_SUPPORTED == True:
				print "Your processor is supported by RHEV 3 Cluster!"
			else:
				print "It seems your processor is not supported by RHEV3 Cluster."
				print "Please try RHEV2 Cluster for this host or contact Red Hat Support."

			sys.exit(0)


def checkCPUAMD():

	RHEV3_SUPPORTED = False
	cpu_family = ""
	model = "0"

	fd = open("/proc/cpuinfo", "r")

	for line in fd.readlines():
		if "cpu family\t" in line:
			value = line.split(':')
			cpu_family = value[1].strip('\n').strip(' ')
		
		if "model\t\t" in line:
			value = line.split(':')
			model = value[1].strip('\n').strip(' ')

		if cpu_family == "15":
			print "Arch: Opteron"
			RHEV3_SUPPORTED = True

		if RHEV3_SUPPORTED == True:
			print "Your processor is supported by RHEV 3 Cluster!"
		else:
			print "It seems your processor is not supported by RHEV3 Cluster."
			print "Please try RHEV2 Cluster for this host or contact Red Hat Support."

		sys.exit(0)

if __name__ == '__main__':

	fd = open("/proc/cpuinfo", "r")

	for line in fd.readlines():
		if "vendor_id" in line:
			if "GenuineIntel" in line:
				checkCPUIntel()
			if "AuthenticAMD" in line:
				checkCPUAMD()
