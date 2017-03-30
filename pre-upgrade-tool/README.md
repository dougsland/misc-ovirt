# Pre-upgrade tool

If you are running the script inside the engine machine no need to use any argument as
the tool will identify engine database information from /etc/ovirt-engine/engine.conf.d/10-setup-database.conf:

``` sh
Example 1, no issues found:

# chmod +x pre-upgrade-tool
# ./pre-upgrade-tool
====================================================
Pre-upgrade tool: 0.1
Connecting to: localhost:5432 Database: engine
====================================================
* Checking for more than one iscsi connection
* Checking running tasks in engine
* Checking for inactive storage...
* Checking for non default engine heap
* Checking for paused vms..
* Checking for non operational hosts
* Checking for vms previewing snapshots
* Checking for 3rd party certs
* Checking for hosts in maintenance mode
* Checking for vms pinned in hosts
* Checking for kerberos sso..
* Checking images locked
* Checking images in illegal mode
* Checking for non default vdsm.conf, persistence=ifcfg
* Checking clusters assigned to datacenters
* Checking for modified engine.conf
* Checking clusters assigned to datacenters

All validation passed, please schedule maintenace window and 
follow the Red Hat Knowledge base about the upgrade process: 
	http://access.redhat.com/article/777777
```

``` sh
Example 2: found a issue

# ./pre-upgrade-check --host 192.168.122.116 --dbuser engine --dbpass T0pS3cr3t! 
                      --dbport 5432 --dbname engine
====================================================
Pre-upgrade tool: 0.1
Connecting to: localhost:5432 Database: test6
====================================================
* Checking for more than one iscsi connection
* Checking running tasks in engine
* Checking for inactive storage...
* Checking for non default engine heap
* Checking for paused vms..
* Checking for non operational hosts
* Checking for vms previewing snapshots
* Checking for 3rd party certs
* Checking for hosts in maintenance mode
* Checking for vms pinned in hosts
* Checking for kerberos sso..
* Checking images locked
* Checking images in illegal mode
* Checking for non default vdsm.conf, persistence=ifcfg
* Checking clusters assigned to datacenters
Cannot execute pre-upgrade tool, please check the following message:
Traceback (most recent call last):
  File "pre-upgrade-check", line 279, in <module>
    preupgrade.check_cluster_no_datacenter()
  File "pre-upgrade-check", line 163, in check_cluster_no_datacenter
    "for more info!".format(ret)
RuntimeError: Found at least one cluster without datacenter assigned!
Query result: [('Prod',)]
Access Knowledge base: http://access.redhat.com/1234567 for more info!
```
