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

import subprocess
import sys
import getopt
import datetime
import os

class Operations:

	def __init__(self):
		self.path = None
		self.selectedOption = None
		self.VERSION = "1.0.0"

	def checkUser(self):
		if os.geteuid() != 0:
			print "You must be root to run this script."
			sys.exit(2)

	def backup(self, path):
		currTime = datetime.datetime.now()

		bkpPath = path +  "/dump_RHEVDB_BACKUP_" + currTime.strftime("%Y-%m-%d-%H:%M") + ".sql"

		print "Backuping database: %s" % (bkpPath)
		cmd = "pg_dump -C -E UTF8 --column-inserts" \
			" --disable-dollar-quoting --disable-triggers -U postgres --format=p -f " + "\"" + bkpPath + "\"" + "rhevm"

		ret = self.runCmd(cmd)
		if ret != 0:
			print "cannot backup rhevm database, please verify!"
			print "Possible options:"
			print "\t - pg_dump command not installed?"
			print "\t - there is no rhevm database"
			print "\t - are you running postgresql service?"
			sys.exit(-1)

	def restore(self, sqlFile):
		print "Restoring database: %s" % (sqlFile)
		cmd = "psql -U postgres -d rhevm -w < " + "\"" + sqlFile + "\""
		ret = self.runCmd(cmd)
		if ret != 0:
			print "cannot restore rhevm database, please verify!"
			print "Possible options:"
			print "\t - psql command not installed?"
			print "\t - there is no rhevm database"
			print "\t - are you running postgresql service?"
			sys.exit(-1)

	def runCmd(self, cmd):
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(output, error) = process.communicate()

		# Let's return the exit value
		return process.poll()

	def stopJboss(self):
		print "Stopping jbossas service..."
		self.runCmd("/sbin/service jbossas stop")
		ret = self.runCmd("/sbin/service jbossas status")
		if ret != 0:
			print "jbossas still running, please stop it before continue!"
			sys.exit(-1)

		return 0

	def startJboss(self):
		print "Starting jbossas service..."
		self.runCmd("/sbin/service jbossas start")
		ret = self.runCmd("/sbin/service jbossas status")
		if ret != 0:
			print "cannot start jbossas service, please verify!"
			sys.exit(-1)

		return 0

	def usage(self):
		print "Usage: " +  sys.argv[0] + " [OPTIONS]"
		print "\t--backup	 \tBackup rhevm* databases" 
		print "\t--restore	 \tRestore database"
		print "\t--path		 \tPath to backup or SQL to restore"
		print "\t--version       \tList version release" 
		print "\t--help          \tThis help menu\n"

		print "Example:"
		print "\t" + sys.argv[0] + " --backup --path=/tmp"
		print "\t" + sys.argv[0] + " --restore --path=/tmp"
		sys.exit(0)

if __name__ == "__main__":

	run = Operations()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "rbp:hv", ["restore", "backup", "path=", "help", "version"])
	except getopt.GetoptError, err:
		# print help info and exit:
		print(err) 
		run.usage()

	for o, a in opts:
		if o in ("-r", "--restore"):
			run.selectedOption = "restore"
		elif o in ("-h", "--help"):
			run.usage()
		elif o in ("-b", "--backup"):
			run.selectedOption = "backup"
		elif o in ("-p", "--path"):
			run.path = a
		elif o in ("-V", "--version"):
			print run.VERSION
			sys.exit(0)
		else:
			assert False, "unhandled option"

	argc = len(sys.argv)

	run.checkUser()

	if argc != 3:
		run.usage()

	if run.selectedOption == None or run.path == None:
		run.usage()

	# Stop Jbossas service
	run.stopJboss()

	if os.path.exists(run.path) == False:
		print "path %s is doesn't exist" % (run.path)

	if run.selectedOption == "backup":
		run.backup(run.path)
	elif run.selectedOption == "restore":
		run.restore(run.path)

	# Start Jbossas service
	run.startJboss()

	print "Done"
