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
        Makefile \
        $(NULL)

dblibdir = $(ovirtdblibpythonlibdir)
pglibdir = $(ovirtdblibpythonlibdir)/pgsql

dblib_PYTHON = \
	__init__.py \
	$(NULL)

pglib_PYTHON = \
	pgsql/__init__.py \
	$(NULL)

clean-local:
	@rm -f Makefile Makefile.in
