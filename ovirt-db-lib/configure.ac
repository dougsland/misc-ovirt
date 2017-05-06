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
define([VERSION_MAJOR], [1])
define([VERSION_MINOR], [0])
define([VERSION_FIX], [0])
define([VERSION_NUMBER], VERSION_MAJOR[.]VERSION_MINOR[.]VERSION_FIX)
define([VERSION_SUFFIX], [_master])

AC_INIT([ovirt-db-lib], VERSION_NUMBER[]VERSION_SUFFIX, [devel@ovirt.org])
PACKAGE_NAME="ovirt-db-lib"
PACKAGE_RPM_VERSION="VERSION_NUMBER"
PACKAGE_RPM_RELEASE="0"
AM_INIT_AUTOMAKE([-Wall -Werror foreign -Wno-portability tar-pax])

AC_SUBST([PACKAGE_RPM_VERSION])
AC_SUBST([PACKAGE_RPM_RELEASE])
AC_SUBST([COMMIT])
AC_SUBST([SHORT_COMMIT])

AC_PROG_INSTALL
AC_PROG_SED
AC_PROG_MAKE_SET
AC_PROG_MKDIR_P
AC_PROG_LN_S

AM_CONDITIONAL(BUILD_PYTHON3, false)

AC_SUBST([preupgradedir], ["\${prefix}/share/ovirt-db-lib/pre-upgrade-sqls"])

AC_PATH_PROG([PYTHON3], [python3], [no])
[if test "$PYTHON3" == "no"]
[then]
    AM_PATH_PYTHON([2])
    AC_SUBST([ovirtdblibpythonlibdir], ["\$(pythondir)/ovirt_db_lib"])
[else]
    AC_SUBST([PYTHON3_PREFIX], ['${prefix}'])
    AC_SUBST([PYTHON3_EXEC_PREFIX], ['${exec_prefix}'])

    PYTHON3_DIR=`$PYTHON3 -c "import distutils.sysconfig; \
        print(distutils.sysconfig.get_python_lib(0,0,prefix='$PYTHON3_PREFIX'))"`
    PYTHON3_EXECDIR=`$PYTHON3 -c "import distutils.sysconfig; \
        print(distutils.sysconfig.get_python_lib(1,0,prefix='$PYTHON3_EXEC_PREFIX'))"`

    AC_SUBST(PYTHON3_CFLAGS)
    AC_SUBST(PYTHON3_LIBS)
    AC_SUBST(python3dir, $PYTHON3_DIR)
    AC_SUBST(py3execdir, $PYTHON3_EXECDIR)
    AC_SUBST([ovirtdblibpythonlibdir], ["\$(python3dir)/ovirt_db_lib"])
[fi]

# Python tools
AC_ARG_VAR([PYFLAKES], [flake8 utility])
AC_CHECK_PROGS([PYFLAKES], [flake8])

AC_CONFIG_FILES([
		Makefile
		src/ovirt_db_lib/Makefile
		src/sqls/pre-upgrade-sqls/Makefile
		ovirt-db-lib.spec])
AC_OUTPUT
