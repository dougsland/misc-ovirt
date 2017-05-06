#!/usr/bin/python
#
# ovirt-db-lib -- ovirt setup library
# Copyright (C) 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import gettext
import os
import psycopg2

from distutils.util import strtobool


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-db-lib')


class Database(object):

    ENGINE_DB_CONF_FILE = (
        '/etc/ovirt-engine/engine.conf.d/10-setup-database.conf'
    )

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(
        self,
        host=None,
        port=None,
        secured=None,
        securedHostValidation=None,
        user=None,
        password=None,
        database=None
    ):
        """
        Connect to database

        Args:
            host - Database host
            port - Database port
            secured -
            securedHostValidation -
            user - Database username
            password - Database password
            database - Database name

            If not argument used, it will try to load the default
            engine database settings from:
              /etc/ovirt-engine/engine.conf.d/10-setup-database.conf

        Returns:
        """

        try:
            engine_data = self.load_engine_credentials
        except:
            raise

        if host is None:
            host = engine_data['host']

        if port is None:
            port = engine_data['port']

        if secured is None:
            secured = engine_data['secured']

        if securedHostValidation is None:
            securedHostValidation = engine_data['secured_validation']

        if user is None:
            user = engine_data['user']

        if password is None:
            password = engine_data['password']

        if database is None:
            database = engine_data['database']

        sslmode = 'allow'
        if secured:
            if securedHostValidation:
                sslmode = 'verify-full'
            else:
                sslmode = 'require'

        try:
            #
            # old psycopg2 does not know how to ignore
            # uselss parameters
            #
            if not host:
                connection = psycopg2.connect(
                    database=database,
                )
            else:
                #
                # port cast is required as old psycopg2
                # does not support unicode strings for port.
                # do not cast to int to avoid breaking usock.
                #
                connection = psycopg2.connect(
                    host=host,
                    port=str(port),
                    user=user,
                    password=password,
                    database=database,
                    sslmode=sslmode,
                )
        except:
            raise

        self.connection = connection

        return connection

    def execute(
        self,
        statement,
        args=dict(),
        host=None,
        port=None,
        secured=None,
        securedHostValidation=None,
        user=None,
        password=None,
        database=None,
        ownConnection=False,
        transaction=True,
    ):
        # autocommit member is available at >= 2.4.2
        def __backup_autocommit(connection):
            if hasattr(connection, 'autocommit'):
                return connection.autocommit
            else:
                return connection.isolation_level

        def __restore_autocommit(connection, v):
            if hasattr(connection, 'autocommit'):
                connection.autocommit = v
            else:
                connection.set_isolation_level(v)

        def __set_autocommit(connection, autocommit):
            if hasattr(connection, 'autocommit'):
                connection.autocommit = autocommit
            else:
                connection.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
                    if autocommit
                    else
                    psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
                )

        ret = []
        old_autocommit = None
        _connection = None
        cursor = None
        try:
            # self.logger.debug(
            #    "Database: '%s', Statement: '%s', args: %s",
            #    database,
            #    statement,
            #    args,
            # )
            if not ownConnection:
                connection = self.connection
            else:
                # self.logger.debug('Creating own connection')

                _connection = connection = self.connect(
                    host=host,
                    port=port,
                    secured=secured,
                    securedHostValidation=securedHostValidation,
                    user=user,
                    password=password,
                    database=database,
                )

            if not transaction:
                old_autocommit = __backup_autocommit(connection)
                __set_autocommit(connection, True)

            if os.path.exists(statement):
                with open(statement, 'r') as f:
                    statement = f.read().strip()

            cursor = connection.cursor()
            cursor.execute(
                statement,
                args,
            )

            if cursor.description is not None:
                cols = [d[0] for d in cursor.description]
                while True:
                    entry = cursor.fetchone()
                    if entry is None:
                        break
                    ret.append(dict(zip(cols, entry)))

        except:
            if _connection is not None:
                _connection.rollback()
            raise
        else:
            if _connection is not None:
                _connection.commit()
        finally:
            if old_autocommit is not None and connection is not None:
                __restore_autocommit(connection, old_autocommit)
            if cursor is not None:
                cursor.close()
            if _connection is not None:
                _connection.close()

        # self.logger.debug('Result: %s', ret)
        return ret

    def disconnect_db(self):
        if self.connection:
            self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect_db()

    def __enter__(
        self,
        host=None,
        port=None,
        secured=None,
        securedHostValidation=None,
        user=None,
        password=None,
        database=None
    ):
        self.connect(
            host,
            port,
            secured,
            securedHostValidation,
            user,
            password,
            database
        )
        return self

    @property
    def load_engine_credentials(self):

        engine_conf = {
            'host': None,
            'port': None,
            'user': None,
            'password': None,
            'database': None,
            'secured': None,
            'secured_validation': None,
            'driver': None,
            'url': None,
        }

        if not os.path.exists(self.ENGINE_DB_CONF_FILE):
            raise RuntimeError(
                _('Unable to find {0}' % self.ENGINE_DB_CONF_FILE)
            )

        with open(self.ENGINE_DB_CONF_FILE) as f:
            for line in f:
                conf_key, conf_value = line.split('=', 1)
                conf_value = conf_value.strip('\n')

                # By default the 10-setup-database.conf includes " "
                # between the values of keys, we should remove it
                conf_value = conf_value[1:-1]

                if 'ENGINE_DB_HOST' == conf_key:
                    engine_conf['host'] = conf_value

                elif 'ENGINE_DB_PORT' == conf_key:
                    engine_conf['port'] = int(conf_value)

                elif 'ENGINE_DB_USER' == conf_key:
                    engine_conf['user'] = conf_value

                elif 'ENGINE_DB_PASSWORD' == conf_key:
                    engine_conf['password'] = conf_value

                elif 'ENGINE_DB_DATABASE' == conf_key:
                    engine_conf['database'] = conf_value

                elif 'ENGINE_DB_SECURED' == conf_key:
                    engine_conf['secured'] = bool(
                            strtobool(conf_value)
                    )

                elif 'ENGINE_DB_SECURED_VALIDATION' == conf_key:
                    engine_conf['secured_validation'] = bool(
                            strtobool(conf_value)
                    )

                elif 'ENGINE_DB_DRIVER' == conf_key:
                    engine_conf['driver'] = conf_value

                elif 'ENGINE_DB_URL' == conf_key:
                    engine_conf['url'] = conf_value

        return engine_conf

# vim: expandtab tabstop=4 shiftwidth=4
