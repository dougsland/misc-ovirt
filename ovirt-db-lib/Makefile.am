# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

AUTOMAKE_OPTIONS = foreign 1.9
ACLOCAL_AMFLAGS = -I m4

PYTHONSOURCES = \
	$(shell find . -name \*.py -o)

SHELL := /bin/bash

SUBDIRS = \
	src/ovirt_db_lib \
	src/sqls/pre-upgrade-sqls \
	$(NULL)	

EXTRA_DIST = \
	ovirt-db-lib.spec \
	ovirt-db-lib.spec.in \
	$(NULL)

DISTCLEANFILES = \
	aclocal.m4 \
	configure \
	install-sh \
	missing \
	py-compile \
	autoscan.log \
	configure.scan \
	$(NULL)

DISTCLEANDIRS = autom4te.cache

TMPREPOS = tmp.repos
RPM_FLAGS := --define="_topdir `pwd`/$(TMPREPOS)"

rpm: srpm
	rpmbuild $(RPM_FLAGS) --rebuild "$(TMPREPOS)"/SRPMS/*.src.rpm
	cp $(distdir).tar.gz $(TMPREPOS)/SOURCES/
	@echo
	@echo "rpm available at '$(TMPREPOS)'"
	@echo


srpm: dist
	rm -rf "$(TMPREPOS)"
	mkdir -vp $(TMPREPOS)/{SPECS,RPMS,SRPMS,SOURCES}
	rpmbuild $(RPM_FLAGS) -ts $(distdir).tar.gz
	@echo
	@echo "srpm available at '$(TMPREPOS)'"

clean-local:
	@rm -rf tmp.repos configure *.log *.spec *.status *.tar.gz *.cache *.scan missing autom4te.cache Makefile.in aclocal.m4 py-compile Makefile install-sh

.PHONY: rpm srpm

check-local: 2to3 flake8
	@echo -e "---\n Passed.\n---"

flake8:
	@for M in $(PYTHONSOURCES); \
	do \
		echo flake8 on "$$M"; \
		PYTHONPATH=. flake8 $$M || exit 1; \
	done

2to3:
	@for M in $(PYTHONSOURCES); \
	do \
		echo 2to3 on "$$M"; \
		PYTHONPATH=. 2to3 $$M || exit 1; \
	done
