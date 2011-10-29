#!/usr/bin/python
#
# Copyright (C) 2011
#
# Douglas Schilling Landgraf <dougsland@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import getopt
import sys
import commands
import os
import socket

# Adding vdsm .pyc libraries to python path
sys.path.append("/usr/share/vdsm")

try:
	import vdscli
except:
	print "Cannot import vdscli, please contact Red Hat support"
	sys.exit(1)

try:
	import vdsClient
except:
	print "Cannot import vdsClient, please contact Red Hat support"
	sys.exit(1)


# General Macros	
VERSION = "1.0.0"
VDSM_PORT = "54321"

class getISCSIid:

	def __init__(self):
		self.useSSL     = None
		self.truststore = None
		self.host       = None

	def do_connect(self, server, port):
		print "Trying to connect to vdsmd host (%s).." % server

		# Connection Validation
		sk = socket.socket()
		try:
			sk.connect((server, int(VDSM_PORT)))
		except Exception, e:
			print "Unable to connect %s" % server 
			sk.close()
			return -1

		self.s = vdscli.connect(server + ':' + port, self.useSSL, self.truststore)

		print "OK, Connected to vdsmd!"
		return 0

	def checkRoot(self):
		if os.geteuid() != 0:
			print "You must be root to run this script."
			sys.exit(2)

	def getStorageInfo(self):

		self.do_connect(self.host, VDSM_PORT)

		try:
			list = self.s.getDeviceList()
		except:
			print "Cannot execute getDeviceList()"
			sys.exit(1)

		if len(list['devList']) == 0:
			print "No storage actived/connected to hypervisor."
			sys.exit(0)

		print "============================================================================"
		for i in range(0, len(list['devList'])):
			print "devList:"
			print "\t vendorID: %s" % (list['devList'][i]['vendorID'])
			print "\t capacity: %s" % (list['devList'][i]['capacity'])
			print "\t fwrev: %s" % (list['devList'][i]['fwrev'])
			print "\t partitioned: %s" % (list['devList'][i]['partitioned'])
			print "\t vgUUID: %s" % (list['devList'][i]['vgUUID'])
			print "\t devtype: %s" % (list['devList'][i]['devtype'])
			print "\t pvUUID: %s" % (list['devList'][i]['pvUUID'])
			print "\t serial: %s" % (list['devList'][i]['serial'])
			print "\t GUID: %s" % (list['devList'][i]['GUID'])
			print "\t productID: %s" % (list['devList'][i]['productID'])

			print "\npathlist:"
			print "\t initiator: %s" % (list['devList'][i]['pathlist'][0]['initiator'])
			print "\t connection: %s" % (list['devList'][i]['pathlist'][0]['connection'])
			print "\t iqn: %s" % (list['devList'][i]['pathlist'][0]['iqn'])
			print "\t portal: %s" % (list['devList'][i]['pathlist'][0]['portal'])
			print "\t user: %s" % (list['devList'][i]['pathlist'][0]['user'])
			print "\t password: %s" % (list['devList'][i]['pathlist'][0]['password'])
			print "\t port: %s" % (list['devList'][i]['pathlist'][0]['port'])

			print "\npathstatus:"
			print "\t physdev: %s" % (list['devList'][i]['pathstatus'][0]['physdev'])
			print "\t type: %s" % (list['devList'][i]['pathstatus'][0]['type'])
			print "\t state: %s" % (list['devList'][i]['pathstatus'][0]['state'])
			print "\t lun: %s" % (list['devList'][i]['pathstatus'][0]['lun'])

			
			#'devtype': 'iSCSI', 'pvUUID': '', 'serial': 'SEMC_LIFELINE-DISK_EMCDSK-200645-55', 'GUID': '35000144f20064555', 'productID': 'LIFELINE-DISK'}

			print "============================================================================"

	def usage(self):
		print "Usage: " +  sys.argv[0] + " [OPTIONS]"
		print "\t--rhevh		\tRHEV-H host which uses/mount the iscsi" 
		print "\t--ssl		 \tTrue or False (vdsm daemon is running with ssl or not?)"
		print "\t--version       \tList version release" 
		print "\t--help          \tThis help menu\n"

		print "Example:"
		print "\t" + sys.argv[0] + " --rhevh 192.168.1.60 --ssl=True"
		sys.exit(1)

if __name__ == "__main__":

	rhevhost   = None
	ssl 	   = None

	VE = getISCSIid()
	try:
		opts, args = getopt.getopt(sys.argv[1:], "r:i:s:hv", ["rhevh=", "iqn=", "ssl=", "help", "version"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print(err) # will print something like "option -a not recognized"
		VE.usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-r", "--rhevh"):
			rhevhost = a
			print ""
		elif o in ("-h", "--help"):
			VE.usage()
			sys.exit()
		elif o in ("-s", "--ssl"):
			ssl = a
		elif o in ("-v", "--version"):
			print VERSION
			sys.exit(0)
		else:
			assert False, "unhandled option"
			sys.exit(-1)

	argc = len(sys.argv)

	if argc != 4:
		VE.usage()

	if rhevhost == None or ssl == None:
		VE.usage()
		sys.exit(-1)

	VE.host   = rhevhost
	VE.useSSL = ssl

	VE.getStorageInfo()
