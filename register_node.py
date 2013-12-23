# Copyright (C) 2012-2013 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

import argparse
import datetime
import glob
import logging
import os
import pwd
import re
import socket
import ssl
import sys

if sys.version_info >= (3, 0):
    import http.client as httplib
else:
    import httplib

import tempfile
import urllib
import urllib2
import urlparse

import M2Crypto
import selinux



try:
    from ovirt.node.utils import fs
except ImportError:
    # Script should continue in case of a non oVirt Node distro
    pass

from vdsm.ipwrapper import routeGet, Route
from vdsm.utils import getHostUUID

log_file = "{0}/{1}-{2}.log".format(
    "/var/log/vdsm",
        datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S"),
        "ovirt-node-registration"
)

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

_LOG = logging.getLogger(__file__)


def _silent_restorecon(path):
    """Execute selinux restorecon cmd to determined file

    Args
    path -- full path to file
    """

    try:
        if selinux.is_selinux_enabled():
            selinux.restorecon(path)
    except:
        _LOG.error("restorecon %s failed" % path)


def register_node(
        url,
        node_hostname,
        node_management_address,
        node_management_port,
        node_uuid
):
    """Register a node to oVirt Engine

    Args
    url -- Engine url
    node_hostname -- Hostname to be registered
    node_management_address -- IP address of node to be registered
    node_management_port -- Communication port between node and engine
    node_uuid -- uuid of node

    Returns
    True (registered) or False
    """
    ret = False

    params = {
        'vds_ip': node_management_address,
        'vds_name': node_hostname,
        'vds_unique_id': node_uuid,
        'port': node_management_port,
    }

    _ENGINE_REG_URIS = (
        '/OvirtEngineWeb/register',
        '/RHEVManagerWeb/VdsAutoRegistration.aspx'
    )
    for uri in _ENGINE_REG_URIS:
        engine_uri = uri + '?' + urllib.urlencode(params)
        reg_url = url + engine_uri

        try:
            _LOG.debug("Trying to register with: %s" % reg_url)
            res = urllib2.urlopen(reg_url)
            if res.getcode() == httplib.OK:
                ret = True
                break
        except urllib2.URLError, e:
            _LOG.info("status: %s code: %s" % (e.reason, e.code))
            if str(httplib.INTERNAL_SERVER_ERROR) in str(e):
                _LOG.info(
                    "Is node already registered? "
                    "hostname: %s url: %s node_management_port: %s uuid: %s" %
                    (
                        node_hostname,
                        url,
                        node_management_port,
                        node_uuid
                    )
                )
                break
    return ret


def _get_remote_public_ssh_key(url):
    """Get public key from determined url

    Args
    url -- URL to download the ssh key

    Returns
    The ssh public key or None in case of failure
    """
    # Regular expression used to validate content of SSH public keys:
    _SSH_PUBLIC_KEY_RE = re.compile(flags=re.VERBOSE, pattern=r"""
 ^
 \s*
 ssh-(rsa|dss)
 \s+
 ([A-Za-z0-9+/]+={0,2})
 (\s+[^\s]+)?
 \s*
 $
""")
    _REMOTE_SSH_KEY_FILE_NAMES = ('engine.ssh.key.txt', 'rhevm.ssh.key.txt')

    authkeys = None
    for key in _REMOTE_SSH_KEY_FILE_NAMES:
        try:
            request = '{0}/{1}'.format(url, key)
            response = urllib2.urlopen(request)
            authkeys = response.read()
        except (urllib2.URLError, urllib2.HTTPError):
            _LOG.info(
                "Cannot locate ssh key at: %s" %
                request
            )
            continue

        if authkeys is not None and \
                _SSH_PUBLIC_KEY_RE.match(authkeys) is not None:
            break

    return authkeys


def _calculate_fingerprint(cert):
    """Calculate fingerprint of certificate

    Args
    cert -- certificate to be calculated the fingerprint

    Returns
    The fingerprint
    """
    x509 = M2Crypto.X509.load_cert_string(cert, M2Crypto.X509.FORMAT_PEM)
    fp = x509.get_fingerprint('sha1')
    fp = ':'.join(fp[pos:pos + 2] for pos in xrange(0, len(fp), 2))

    return fp


def _insert_ssh_key(key_file_name, key):
    """Insert the downloaded public ssh key into authorized key file

    Args
    key_file_name - full path to authorized key file
    key - String of public ssh key

    """
    keys = []

    if os.path.exists(key_file_name):
        for line in open(key_file_name):
            if not line.endswith('\n'):
                line += '\n'

            if line != '\n' and not line.endswith(" ovirt-engine\n") or \
                    line.startswith("#"):
                keys.append(line)

    if not key.endswith('\n'):
        key += '\n'

    keys.append(key)

    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(key_file_name),
        delete=False
    ) as f:
        f.write(''.join(keys))

    if os.path.exists('/etc/rhev-hypervisor-release') or \
            glob.glob('/etc/ovirt-node-*-release'):
        fs.Config().unpersist(key_file_name)

    os.rename(f.name, key_file_name)

    if os.path.exists('/etc/rhev-hypervisor-release') or \
            glob.glob('/etc/ovirt-node-*-release'):
        fs.Config().persist(key_file_name)


def _add_authorized_ssh_key(key):
    """Check the dependencies, like creation ssh dir, chmod,
       persist file in case of ovirt node and selinux stuff to insert the
       ssh public key to authorized key file

    Args
    key - String of public ssh key

    """
    _PATH_ROOT_SSH = pwd.getpwnam('root').pw_dir + '/.ssh'
    _PATH_ROOT_AUTH_KEYS = _PATH_ROOT_SSH + '/authorized_keys'

    if not os.path.exists(_PATH_ROOT_SSH):
        os.mkdir(_PATH_ROOT_SSH, 0o700)
        _silent_restorecon(_PATH_ROOT_SSH)

    _insert_ssh_key(_PATH_ROOT_AUTH_KEYS, key)

    os.chmod(_PATH_ROOT_AUTH_KEYS, 0o644)
    _silent_restorecon(_PATH_ROOT_AUTH_KEYS)

    if os.path.exists('/etc/rhev-hypervisor-release') or \
            glob.glob('/etc/ovirt-node-*-release'):
        fs.Config().persist(_PATH_ROOT_AUTH_KEYS)


def main():
    """
    Register node to engine
    """

    _DEFAULT_NODE_MANAGEMENT_PORT = 54321

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Tool to register node to oVirt Engine',
        epilog='Example of use:\n%(prog)s '
                    '--authorize-engine-ssh-key '
                    '--url https://ovirtengine.localdomain:443 '
                    '--fingerprint DC:B9:67:35:60:FC:29:E4:C8:03:4E:5:7A:0D '
                    '--node-management-address 10.10.1.1 '
                    '--node-management-port 54321'
    )

    parser.add_argument(
        '--authorize-engine-ssh-key',
        action='store_true',
        help='Add ovirt engine public ssh key to node authorized keys',
    )

    parser.add_argument(
        '--fingerprint',
        help="Fingerprint to be validate against engine web CA"
    )

    parser.add_argument(
        '--hostname',
        help="Speficy the human-readable name of the node being registered"
    )

    parser.add_argument(
        '--skip-fingerprint',
        action='store_true',
        help='Skip fingerprint check',
    )

    parser.add_argument(
        '--node-management-address',
        help="Node IP address to be registered",
    )

    parser.add_argument(
        '--node-management-port',
        help="Node management port",
    )

    parser.add_argument(
        '--node-uuid',
        help="Provide an explicit host uuid"
    )

    parser.add_argument(
        '--url',
        help="Engine URL",
        required=True
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="verbose mode, set logging to DEBUG instead of ERROR"
    )
    args = parser.parse_args()

    url = urlparse.urlparse(args.url)
    url_port = url.port

    if url.scheme == "https" and url_port is None:
        url_port = 443
    elif url.scheme == "http" and url_port is None:
        url_port = 80

    if url.scheme == "https" and args.fingerprint:
        engine_cert = ssl.get_server_certificate(
            (
                url.hostname,
                int(url_port)
            )
        )

    if not args.skip_fingerprint and args.fingerprint is None:
        raise RuntimeError('You must use --fingerprint or --skip-fingerprint')

    if args.verbose:
        logging.setLevel(logging.DEBUG)

    if not args.skip_fingerprint and url.scheme == "https":
        cert_fingerprint = _calculate_fingerprint(engine_cert)
        if not args.fingerprint.lower() == cert_fingerprint.lower():
            str_error = "Fingerprint {0} doesn't match " \
                "server's fingerprint!".format(
                    args.fingerprint.lower(),
                )
            _LOG.debug(str_error)
            raise RuntimeError(str_error)

    if args.fingerprint and url.scheme == "http":
        _LOG.debug("Skipping fingerprint check, user provided http url")

    if args.authorize_engine_ssh_key:
        key = _get_remote_public_ssh_key(args.url)
        if key is not None:
            _add_authorized_ssh_key(key)
        else:
            _LOG.error(
                "Cannot download public ssh key from %s" % args.url
            )

    node_uuid = args.node_uuid
    if node_uuid is None:
        node_uuid = getHostUUID(False)
        if node_uuid is None:
            raise RuntimeError('Cannot retrieve host UUID')

    node_hostname = args.hostname
    if node_hostname is None:
        node_hostname = socket.gethostname()

    management_port = args.node_management_port
    if management_port is None:
        management_port = _DEFAULT_NODE_MANAGEMENT_PORT

    node_management_address = args.node_management_address
    if node_management_address is None:
        route = routeGet([urlparse.urlparse(args.url).hostname])[0]
        node_management_address = Route.fromText(route).src

    if register_node(
            args.url,
            node_hostname,
            node_management_address,
            int(management_port),
            node_uuid
    ):
        _LOG.info(
            "Registration is completed: url: %s, hostname: %s "
            "management address: %s management port: %s" %
            (
                args.url,
                node_hostname,
                node_management_address,
                management_port
            )
        )
    else:
        raise RuntimeError('Cannot complete the registration')

if __name__ == '__main__':
    main()
