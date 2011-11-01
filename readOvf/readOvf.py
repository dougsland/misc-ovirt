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

import sys
from xml.etree import ElementTree



if len(sys.argv) != 2:
	print "Use: %s file.ovf" % (sys.argv[0])
	sys.exit(0)


xmldata = ""
xmldata += open(sys.argv[1]).read()

tree = ElementTree.XML(xmldata)
list = tree.findall("Content")

print "\nReading Content:"
print "=================================\n"
for item in list:
	#print "\tovf:id: %s" % (item.attrib['{http://schemas.dmtf.org/ovf/envelope/1/}id'])
	#print "\txsi type: %s" % (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'])

	print "\tName: %s"			% (item.find("Name").text)

	if (item.find("TemplateId")):
		print "\tTemplateId: %s"		% (item.find("TemplateId").text)

	if (item.find("TemplateName")):
		print "\tTemplateName: %s"		% (item.find("TemplateName").text)

	print "\tDescription: %s"		% (item.find("Description").text)

	if (item.find("Domain")):
		print "\tDomain: %s"			% (item.find("Domain").text)

	print "\tCreation Date: %s"		% (item.find("CreationDate").text)

	if (item.find("IsInitilized")):
		print "\tIsInitilized: %s"		% (item.find("IsInitilized").text)

	if (item.find("IsAutoSuspend")):
		print "\tIsAutoSuspend: %s"		% (item.find("IsAutoSuspend").text)

	if (item.find("TimeZone")):
		print "\tTimeZone: %s"			% (item.find("TimeZone").text)

	if (item.find("IsStateless")):
		print "\tIsStateless: %s"		% (item.find("IsStateless").text)

	if (item.find("Origin")):
		print "\tOrigin: %s"			% (item.find("Origin").text)

	
	if (item.find("default_boot_sequence")):
		print "\tdefault_boot_sequence: %s"	% (item.find("default_boot_sequence").text)

	print "\tVmType: %s"			% (item.find("VmType").text)

	if (item.find("DefaultDisplayType")):
		print "\tDefaultDisplayType: %s"	% (item.find("DefaultDisplayType").text)

	if (item.find("MinAllocatedMem")):
		print "\tMinAllocatedMem: %s"		% (item.find("MinAllocatedMem").text)

	listCS = tree.findall("Content/Section")
	for item in listCS:
		if (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type']) == "ovf:OperatingSystemSection_Type":
			print "\n\tReading Content/Section [OperationSystem]"
			print "\t=============================================="
			print "\n\t\tInfo: %s" % (item.find("Info").text)
			print "\t\tDescription: %s" % (item.find("Description").text)

		if (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type']) == "ovf:VirtualHardwareSection_Type":
			print "\n\tReading Content/Section [VirtualHardware]"
			print "\t=============================================="
			print "\n\t\tInfo: %s" % (item.find("Info").text)
			for syst in (item.find("System")):
				if syst.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData}VirtualSystemType":
					print "\t\tVirtualSystemType: %s" %(syst.text)

print "\n\tReading Content/Section/Item:"
print "\t=================================\n"
listItem  = tree.findall("Content/Section/Item")
for items in listItem:
	for itemContent in items:
		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Caption":
			print "\n\tCaption: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Description":
			print "\tDescription: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}InstanceId":
			print "\tInstanceId: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}ResourceType":
			print "\tResourceType: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}num_of_sockets":
			print "\tnum_of_sockets: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}cpu_per_socket":
			print "\tcpu_per_socket: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}AllocationUnits":
			print "\tAllocationUnits: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}VirtualQuantity":
			print "\tVirtualQuantity: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}HostResource":
			print "\tHostResource: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Parent":
			print "\tParent: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Template":
			print "\tTemplate: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}ApplicationList":
			print "\tApplicationList: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}StorageId":
			print "\tStorageId: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}StoragePoolId":
			print "\tStoragePoolId: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}CreationDate":
			print "\tCreationDate: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}LastModified":
			print "\tLastModified: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}last_modified_date":
			print "\tlast_modified_date: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}ResourceSubType":
			print "\tResourceSubType: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Connection":
			print "\tConnection: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Name":
			print "\tName: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}MACAddress":
			print "\tMACAddress: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}speed":
			print "\tspeed: %s" %(itemContent.text)

		if itemContent.tag == "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}UsbPolicy":
			print "\tUsbPolicy: %s" %(itemContent.text)

list = tree.findall("Section")
for item in list:

	if (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type']) == "ovf:NetworkSection_Type":
		print "\nReading Network Section"
		print "================================="
		#print "\n\txsi:type: %s" % (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'])
		print "\n\tInfo: %s" % (item.find("Info").text)
		print "\tName: %s" % (item.find("Network").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}name'])

	if (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type']) == "ovf:DiskSection_Type":
		print "\n\bReading Disk Section"
		print "================================="
		#print "\n\txsi:type: %s" % (item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'])
		print "\n\tInfo: %s" % (item.find("Info").text)
		print "\twipe-after-delete: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}wipe-after-delete'])
		print "\tformat: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}format'])
		print "\tvm_snapshot_id: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}vm_snapshot_id'])
		print "\tparentRef: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}parentRef'])
		print "\tfileRef: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}fileRef'])
		print "\tactual_size: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}actual_size'])
		print "\tvolume-format: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}volume-format'])
		print "\tboot: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}boot'])
		print "\tsize: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}size'])
		print "\tvolume-type: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}volume-type'])
		print "\tdisk-type: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}disk-type'])
		print "\tdiskId: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}diskId'])
		print "\tdisk-interface: %s" % (item.find("Disk").attrib['{http://schemas.dmtf.org/ovf/envelope/1/}disk-interface'])

