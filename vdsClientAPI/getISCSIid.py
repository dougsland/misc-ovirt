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
from iniparse import ConfigParser

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
		self.iqn        = None

	def do_connect(self, server, port):
		print "Trying to connect to vdsmd host (%s).." % server

		# Connection Validation
		sk = socket.socket()

		# Timeout 8 sec
		sk.settimeout(8)
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

	def checkSPM(self):

		found = False 

		self.do_connect(self.host, VDSM_PORT)

		try:
			list = self.s.getDeviceList()
		except:
			print "Cannot execute getDeviceList()"
			sys.exit(1)

		for i in range(0, len(list['devList'])):
			if list['devList'][i]['pathlist'][0]['iqn'] == self.iqn:
				print list['devList'][i]['GUID']
				found = True

		if found == False:
			print "iqn not found!"

	def usage(self):
		print "Usage: " +  sys.argv[0] + " [OPTIONS]"
		print "\t--rhevh		\tRHEV-H host which uses/mount the iscsi" 
		print "\t--iqn		 \tiscsi iqn"
		print "\t--ssl		 \tTrue or False (vdsm daemon is running with ssl or not?)"
		print "\t--version       \tList version release" 
		print "\t--help          \tThis help menu\n"

		print "Example:"
		print "\t" + sys.argv[0] + " --rhevh 192.168.1.60 --ssl=True --iqn iqn.1992-04.com.emc:storage.storage.iscsidata"
		sys.exit(1)

if __name__ == "__main__":

	rhevhost   = None
	iqnaddress = None
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
		elif o in ("-i", "--iqn"):
			iqnaddress = a
		elif o in ("-V", "--version"):
			print VERSION
			sys.exit(0)
		else:
			assert False, "unhandled option"
			sys.exit(-1)

	argc = len(sys.argv)

	if argc != 6:
		VE.usage()

	if rhevhost == None or iqnaddress == None or ssl == None:
		VE.usage()
		sys.exit(-1)

	VE.host   = rhevhost
	VE.iqn    = iqnaddress
	VE.useSSL = ssl

	VE.checkSPM()
