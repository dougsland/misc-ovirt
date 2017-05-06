# -*- coding: utf-8 -*-
#
# Copyright (C) 2017
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
MAINTAINERCLEANFILES = \
        Makefile.in \
        $(NULL)

predir = $(preupgradedir)

pre_DATA = \
	cluster/cluster_query_check_datacenter.sql \
	engine/engine_versions_through_all_upgrades.sql \
	hosts/hosts_create_related_lookup_tables.sql \
	hosts/hosts_query_check_health.sql \
	network/networks_table_not_using_network_attachments.sql \
	network/networks_table_using_network_attachments.sql \
	storage/storage_create_related_lookup_tables.sql \
	vms/vms_create_related_lookup_tables.sql \
	vms/vms_query_health.sql \
	cleanup.sql \
	$(NULL)

EXTRA_DIST = \
	cluster \
	engine \
	hosts \
	network \
	storage \
	vms \
	cleanup.sql \
	$(NULL)

clean-local:
	@rm -f Makefile Makefile.in
