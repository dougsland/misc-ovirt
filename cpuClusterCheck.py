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

def checkCPUIntel(cpuFileDescriptor):

	RHEV3_SUPPORTED = False
	cpu_family = ""
	model = "0"

	cpuFileDescriptor.seek(0)

	for line in cpuFileDescriptor.readlines():
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

				if model == "22" or model == "15" or model == "42":
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

			cpuFileDescriptor.close()
			sys.exit(0)

	cpuFileDescriptor.close()
	sys.exit(1)


def checkCPUAMD(cpuFileDescriptor):

	RHEV3_SUPPORTED = False
	cpu_family = ""
	model = "0"

	cpuFileDescriptor.seek(0)

	for line in cpuFileDescriptor.readlines():
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

		cpuFileDescriptor.close()
		sys.exit(0)

	cpuFileDescriptor.close()
	sys.exit(1)

if __name__ == '__main__':

	try:
		fd = open("/proc/cpuinfo", "r")
	except IOError:
		print "Error: unable to open /proc/cpuinfo"
		sys.exit(1)

	for line in fd.readlines():
		if "vendor_id" in line:
			if "GenuineIntel" in line:
				checkCPUIntel(fd)
			if "AuthenticAMD" in line:
				checkCPUAMD(fd)

	print "Error: unsupported vendor_id"
	fd.close()
	sys.exit(1)
