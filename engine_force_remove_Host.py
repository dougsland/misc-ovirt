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

import psycopg2
import sys

DBPASS = "my_db_pass"

def removeHost(host):  

	try:
		con = psycopg2.connect("dbname='engine' user='postgres' password='" + DBPASS + "'")
	except:
		print "aborting.. unable to connect to the database.. bad password?"
		sys.exit(-1)

	cursor = con.cursor()
	cmd    = "select vds_id from vds_static where vds_name='" + host + "'"
	try:
		cursor.execute(cmd)
	except:
		print "Cannot execute select into vds_static" %(host)
		sys.exit(-1)

	ret = cursor.fetchone()
	if ret == None:
		print "Cannot locate host %s" %(host)
		sys.exit(-1)

	vds_id = ret[0]

	cmd = "delete from vds_statistics where vds_id='" + vds_id + "'"
	try:
		cursor.execute(cmd)
	except:
		print "Cannot remove entry from vds_statistics"
		sys.exit(-1)

	con.commit()

	cmd = "delete from vds_dynamic where vds_id='" + vds_id + "'"
	try:
		cursor.execute(cmd)
	except:
		print "Cannot remove entry from vds_dynamic"
		sys.exit(-1)

	con.commit()

	cmd = "delete from vds_static where vds_id='" + vds_id + "'"
	try:
		cursor.execute(cmd)
	except:
		print "Cannot remove entry from vds_static"
		sys.exit(-1)

	con.commit()

	print "Done!"

if __name__ == "__main__":

	if len(sys.argv) != 2:
        	print "%s HOST" % (sys.argv[0])
		sys.exit(-1)


	print "This is *NOT* supported operation"
	ans = raw_input("Are you sure you want to continue? (yes/no) ")

	if ans != "yes":
		print "aborting..."
		sys.exit(2)

	print "Removing host %s..." % (sys.argv[1])
	removeHost(sys.argv[1])
