#!/usr/bin/env python
#
# Copyright 2010
#
# Licensed to you under the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Require Packages: python-iniparse
#
# Original script by:
# - Douglas Landgraf (dougsland@gmail.com)
# - Vladik Romanovsky (vladik.romanovsky@gmail.com)
#
# Contributors:
# - Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)


###############################################################################
##############                       WARNING                     ##############
##############   The use of this script is inherently raceful    ##############
##############   use it only on emergency cases when it's no     ##############
##############   possible to wait until manager  is up again     ##############
###############################################################################


import getopt
import sys
import commands
import os
import socket
from xml.dom.minidom import parse, parseString

try:
    from iniparse import ConfigParser
except:
    print "Package python-iniparse is required, please install"
    print "#yum install python-iniparse -y"
    sys.exit(1)

try:
    from vdsm import vdscli
except:
    print "Cannot import vdscli, please fix it"
    sys.exit(1)

try:
    import vdsClient
except:
    print "Cannot import vdsClient, please fix it"
    sys.exit(1)

# General Macros
VERSION = "1.0.0"

#DEBUG MODE
DEBUG = "False"  # True or False

#########################################################################


class vdsmEmergency:

    def __init__(self):
        """Initialize method"""
        sslRet = self.checkSSLvdsm()
        self.useSSL = sslRet
        self.truststore = None

    def do_connect(self, server, port):
        """Do a connection with vdsm daemon"""
        print "Trying to connect to vdsmd host (%s).." % server

        # Connection Validation
        sk = socket.socket()
        try:
            sk.connect((server, int(VDSM_PORT)))
        except Exception, e:
            print "Unable to connect %s" % server
            sk.close()
            return -1

        self.conn_info = vdscli.connect(server + ':' + port, self.useSSL,
                                        self.truststore)

        print "OK, Connected to vdsmd!"
        return 0

    def checkRoot(self):
        """check if the user running the script is root"""
        if os.geteuid() != 0:
            print "You must be root to run this script."
            sys.exit(2)

    def getIpManagementIP(self):
        """get the IP from management interface"""

        # TODO: avoid this kind of hack, find a better approach (vdsClient
        # provide the IP of ovirtmgmt/rhevm interface?)
        #
        # Code to make it work for the rhevm or the ovirtmgmt interface

        strCmd = ("ifconfig ovirtmgmt 2>/dev/null|grep inet|grep -v inet6|" +
                  "awk '{print $2}'|cut -d ':' -f2")
        retCmd = commands.getstatusoutput(strCmd)
        if retCmd[1] == "":
            strCmd = ("ifconfig rhevm 2>/dev/null|grep inet|grep -v inet6|" +
                      "awk '{print $2}'|cut -d ':' -f2")
            retCmd = commands.getstatusoutput(strCmd)

        if retCmd[0] != 0:
            print "Error getting IP from management interface"
            sys.exit(1)

        return retCmd[1]

    def checkSSLvdsm(self):
        """check if vdsm is running as SSL or without it"""

        cfg = ConfigParser()
        cfg.read('/etc/vdsm/vdsm.conf')
        cfg.get('vars', 'ssl')

        return cfg.data.vars.ssl

    def checkVmRunning(self, otherHostsList, VmsToStart):
        """check if the vm's are running"""

        hosts = None
        vms = None
        i = 0
        j = 0

        if otherHostsList is None:
            return -1

        if VmsToStart is None:
            return -1

        vms = VmsToStart.split(",")
        hosts = otherHostsList.split(",")

        # Let's check if all other Hosts are running the VirtualMachine
        while (i != len(hosts)):
            ret = VE.do_connect(hosts[i], VDSM_PORT)
            if ret < 0:
                sys.exit(1)
            response = self.s.list()
            if response['status']['code'] != 0:
                print ("cannot execute list operation, err:" +
                       response['status']['message'])

            # Checking VM status
            for s in self.s.getAllVmStats()['statsList']:
                j = 0

                # print all vms in each host
                while j < len(vms):
                    if DEBUG == "True":
                        print len(vms)
                        print s['vmId']
                        print hosts[i]
                        print vms[j]

                    vmIdCurr = self.getVmId(vms[j])

                    if DEBUG == "True":
                        print vmIdCurr
                        print s['vmId']

                    if s['vmId'] == vmIdCurr and s['status'] == "Up":
                        print ("Cannot continue, the VM %s is running" +
                               " in host %s" % (vms[j], hosts[i]))
                        sys.exit(1)
                    j = j + 1

            # counter for hosts
            i = i + 1

        print ("OK, the vm(s) specified are not running on the host(s)" +
               " informed, continuing..")

    def checkSPM(self):
        """check if the host which is running this script is the SPM"""
        self.spUUID = None
        self.spmStatus = None

        ip_management_interface = self.getIpManagementIP()
        self.do_connect(ip_management_interface, VDSM_PORT)

        try:
            list = self.s.getConnectedStoragePoolsList()
        except:
            print "Cannot execute getConnectedStoragePoolsList()"
            sys.exit(1)

        # Shu Ming comments that this may not make any sense as it seems to
        # be always the last entry FIXME

        for entry in list['poollist']:
            self.spUUID = entry

        if not self.spUUID:
            print "Cannot locate Storage Pools List.. aborting!"
            sys.exit(1)

        try:
            status = self.s.getSpmStatus(self.spUUID)
        except:
            print "Cannot execute getSpmStatus()"
            sys.exit(1)

        self.spmStatus = status['spm_st']['spmStatus']

        if self.spmStatus != "SPM":
            print ("This host is not the current SPM, " +
                   "status [%s]" % self.spmStatus)
            sys.exit(1)

    def getVmId(self, vmName):
        """get the vmId from the vmName used as argument"""
        path = "/rhev/data-center/%s/mastersd/master/vms" % (self.spUUID)

        # First verify which domainID contain de XML files
        try:
            dirList = os.listdir(path)
        except:
            print "Cannot locate the dir with ovf files.. aborting!"
            sys.exit(1)

        #Read all content of xml(s) file(s)
        for fname in dirList:

            pathOVF = path + "/" + fname + "/" + fname + ".ovf"

            dom = parse(pathOVF)

            # Getting vmId field
            i = 0
            attr = 0
            for node in dom.getElementsByTagName('Section'):
                while (i < len(node.attributes)):
                    attr = node.attributes.items()
                    if attr[i][0] == "ovf:id":
                        vmId = attr[i][1]
                    i = i + 1

            # Getting vmName field
            for node in dom.getElementsByTagName('Content'):
                if node.childNodes[0].firstChild is not None:
                    if node.childNodes[0].firstChild.nodeValue == vmName:
                        return vmId

    def _parseDriveSpec(self, spec):
        if ',' in spec:
            d = {}
            for s in spec.split(','):
                k, v = s.split(':', 1)
                if k == 'domain':
                    d['domainID'] = v
                if k == 'pool':
                    d['poolID'] = v
                if k == 'image':
                    d['imageID'] = v
                if k == 'volume':
                    d['volumeID'] = v
                if k == 'boot':
                    d['boot'] = v
                if k == 'format':
                    d['format'] = v
            return d
        return spec

    def readXML(self, VmsStotart, destHostStart):
        """read all xml available pointed to Directory path and parse for
        specific fields"""

        # number of Vms found
        nrmVms = 0
        cmd = {}
        # Path to XML files
        # example default path:
        # /rhev/data-center/1a516f64-f091-4785-9278-362037513408/vms
        path = "/rhev/data-center/%s/mastersd/master/vms" % (self.spUUID)

        # First verify which domainID contain de XML files
        try:
            dirList = os.listdir(path)
        except:
            print "Cannot locate the dir with ovf files.. aborting!"
            sys.exit(1)

        # FIXME: The following loop code is iterating over files as well as
        # starting VM's, this should be converted to a function

        #Read all content of xml(s) file(s)
        for fname in dirList:

            pathOVF = path + "/" + fname + "/" + fname + ".ovf"
            cmd['display'] = "vnc"
            cmd['kvmEnable'] = "True"
            cmd['tabletEnable'] = "True"
            cmd['vmEnable'] = "True"
            cmd['irqChip'] = "True"
            cmd['nice'] = 0
            cmd['keyboardLayout'] = "en-us"
            cmd['acpiEnable'] = "True"
            cmd['tdf'] = "True"

            dom = parse(pathOVF)

            # Getting vmId field
            i = 0
            attr = 0
            for node in dom.getElementsByTagName('Section'):
                while (i < len(node.attributes)):
                    attr = node.attributes.items()
                    if attr[i][0] == "ovf:id":
                        cmd["vmId"] = attr[i][1]
                    i = i + 1

            # Getting vmName field
            for node in dom.getElementsByTagName('Content'):
                if node.childNodes[0].firstChild is not None:
                    self.vmName = node.childNodes[0].firstChild.nodeValue
                    cmd['vmName'] = self.vmName

            # Getting image and volume
            i = 0
            attr = 0
            for node in dom.getElementsByTagName('Disk'):
                while (i != len(node.attributes)):
                    attr = node.attributes.items()
                    if attr[i][0] == "ovf:fileRef":
                        storage = attr[i][1]
                        data = storage.split("/")
                        image = data[0]
                        volume = data[1]
                    i += 1

            # Getting VM format, boot
            i = 0
            attr = 0
            for node in dom.getElementsByTagName('Disk'):
                while (i != len(node.attributes)):
                    attr = node.attributes.items()
                    if attr[i][0] == "ovf:volume-format":
                        format = attr[i][1]

                    if attr[i][0] == "ovf:boot":
                        vmBoot = attr[i][1]

                    if attr[i][0] == "ovf:disk-interface":
                        ifFormat = attr[i][1]

                    i += 1

            if format == "COW":
                vmFormat = ":cow"
            elif format == "RAW":
                vmFormat = ":raw"

            if ifFormat == "VirtIO":
                ifDisk = "virtio"
            elif ifFormat == "IDE":
                ifDisk = "ide"
            drives = []
            # Getting Drive, bridge, memSize, macAddr, smp, smpCoresPerSocket
            for node in dom.getElementsByTagName('Item'):
                # Getting Drive
                if node.childNodes[0].firstChild is not None:
                    str = node.childNodes[0].firstChild.nodeValue
                    if str.find("Drive") > -1:
                        tmp = ("pool:" + self.spUUID + ",domain:" +
                               node.childNodes[7].firstChild.nodeValue +
                               ",image:" + image + ",volume:" + volume +
                               ",boot:" + vmBoot + ",format" + vmFormat +
                               ",if:" + ifDisk)
                        #param,value = tmp.split("=",1)
                        drives += [self._parseDriveSpec(tmp)]
                        cmd['drives'] = drives

                # Getting bridge
                nicMod = None

                if node.childNodes[0].firstChild.nodeValue == ("Ethernet" +
                                                               "adapter on" +
                                                               " rhevm"):

                    if node.childNodes[3].firstChild.nodeValue == "3":
                        nicMod = "pv"       # VirtIO
                    elif node.childNodes[3].firstChild.nodeValue == "2":
                        nicMod = "e1000"    # e1000
                    elif node.childNodes[3].firstChild.nodeValue == "1":
                        nicMod = "rtl8139"  # rtl8139

                    cmd['nicModel'] = nicMod
                    cmd['bridge'] = node.childNodes[4].firstChild.nodeValue

                # Getting memSize field
                str = node.childNodes[0].firstChild.nodeValue
                if str.find("MB of memory") > -1:
                    cmd['memSize'] = node.childNodes[5].firstChild.nodeValue

                # Getting smp and smpCoresPerSocket fields
                str = node.childNodes[0].firstChild.nodeValue
                if str.find("virtual cpu") > -1:
                    cmd["smp="] = node.childNodes[4].firstChild.nodeValue
                    cmd["smpCoresPerSocket"] = (
                        node.childNodes[5].firstChild.nodeValue)

                # Getting macAddr field
                if node.childNodes[0].firstChild.nodeValue == ("Ethernet" +
                                                               " adapter on" +
                                                               " rhevm"):
                    if len(node.childNodes) > 6:
                        cmd['macAddr'] = (
                            node.childNodes[6].firstChild.nodeValue)

                    # if node.childNodes < 6 it`s a template entry, so ignore
                    if len(node.childNodes) > 6:
                        # print only vms to start
                        try:
                            checkvms = VmsToStart.split(",")
                        except:
                            print "Please use , between vms name, avoid space"
                            self.usage()

                        i = 0
                        while (i != len(checkvms)):
                            if self.vmName == checkvms[i]:
                                nrmVms = nrmVms + 1
                                self.startVM(cmd, destHostStart)
                            i += 1

        print "Total VMs found: %s" % nrmVms

    def startVM(self, cmd, destHostStart):
        """start the VM"""

        self.do_connect(destHostStart, VDSM_PORT)
        #print cmd
        #cmd1 = dict(cmd)
        #print cmd1
        ret = self.s.create(cmd)
        #print ret
        print "Triggered VM [%s]" % self.vmName

    def usage(self):
        """shows the program params"""
        print "Usage: " + sys.argv[0] + " [OPTIONS]"
        print "\t--destHost      \t Hypervisor host which will start the VM"
        print "\t--otherHostsList\t All remaining hosts"
        print "\t--vms           \t Specify the Names of which VMs to start"
        print "\t--version        \t List version release"
        print "\t--help           \t This help menu\n"
        print "\t--port           \t Specify port to use, default is 54321"

        print "Example:"
        print ("\t" + sys.argv[0] + " --destHost LinuxSrv1 --otherHostsList" +
               " Megatron,Jerry --vms vm1,vm2,vm3,vm4 --port 54321")
        sys.exit(1)


if __name__ == "__main__":

    otherHostsList = ''
    VmsToStart = None
    destHostStart = None
    VDSM_PORT = 54321

    VE = vdsmEmergency()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "Vd:ho:v:", ["destHost=",
                                   "otherHostsList=", "vms=", "help",
                                   "version", "port"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        VE.usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-d", "--destHost"):
            destHostStart = a
            print ""
        elif o in ("-h", "--help"):
            VE.usage()
            sys.exit()
        elif o in ("-o", "--otherHostsList"):
            otherHostsList = a
        elif o in ("-v", "--vms"):
            VmsToStart = a
        elif o in ("--port"):
            VDSM_PORT = a
        elif o in ("-V", "--version"):
            print VERSION
        else:
            assert False, "unhandled option"

    argc = len(sys.argv)
    if argc < 2:
        VE.usage()

    VE.checkSPM()

    # Include the destHost to verify
    otherHostsList += ",%s" % destHostStart
    VE.checkVmRunning(otherHostsList, VmsToStart)

    VE.readXML(VmsToStart, destHostStart)
