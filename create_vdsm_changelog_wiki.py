#!/usr/bin/python
#
# Copyright (C) 2014
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import argparse
import os
import re
import subprocess
import time
import xmlrpclib
import xml.parsers.expat

import bugzilla

_BUGZILLA_USER = None
_BUGZILLA_PASS = None

_XMLRPC_ERR_BUG_DOEST_EXIST = 101
_XMLRPC_ERR_CONNECTION_PROBLEM = 18
_XMLRPC_ERR_SSL_CONNECTION = 35

_LOG_FILE_NAME = "git_log.txt"
_DEFAULT_TARGET_RELEASE = "---"

_CMD_GET_BRANCHES = "git branch -a | cut -f 3 -d '/' | egrep ^ovirt |" \
    " sort -r | cut -f 2 -d '-'"

# Creates a List of dictionaries
bz_data = {}
list_bz_data = []


def bugzilla_login():
    """Executes bugzilla
    Returns python-bugzilla object
    """
    bug_rh_url = bugzilla.Bugzilla(
        url="https://bugzilla.redhat.com/xmlrpc.cgi"
    )

    if not bug_rh_url.login(_BUGZILLA_USER, _BUGZILLA_PASS):
        raise RuntimeError("Cannot login into the bugzilla account provided!")

    return bug_rh_url


def run_cmd(cmd):
    """Executes a command

    Args:
    cmd - Command to be executed

    Returns
    output
    """
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    (output, error) = process.communicate()

    return output


def collect_bugzilla_data():
    """Collect bugzilla data, like id, title, target release and status
    """
    bug_rh_url = bugzilla_login()
    with open(_LOG_FILE_NAME, "r") as fd:
        retry = False
        for line in fd:
            if "bug-url" in line.lower():
                try:
                    bug_url = line.lower().split("bug-url:")[1].strip()
                except IndexError:
                    pass

                bug_id = ''.join(re.findall(r'\d+', bug_url))

                if not bug_id:
                    continue

                try:
                    bug_info = bug_rh_url.getbug(bug_id)
                except xmlrpclib.Fault as errFault:
                    if errFault.faultCode == _XMLRPC_ERR_BUG_DOEST_EXIST:
                        continue
                except xmlrpclib.ProtocolError as errProto:
                    if errProto.errcode == _XMLRPC_ERR_CONNECTION_PROBLEM or \
                            errProto.errcode == _XMLRPC_ERR_SSL_CONNECTION:
                        retry = True
                except xml.parsers.expat.ExpatError:
                    # Bugzilla delay generates
                    # xml.parsers.expat.ExpatError:
                    # syntax error: line 1, column 49
                    retry = True

                if retry:
                    retry = False
                    print "Package dropped with server. trying again in 5m" \
                        " - bugid [%s]" % bug_id
                    print "Logout bugzilla account.."
                    bug_rh_url.logout()
                    print "Sleeping.."
                    time.sleep(300)
                    print "Executing new login and collecting data again.."
                    bug_rh_url = bugzilla_login()
                    bug_info = bug_rh_url.getbug(bug_id)

                bug_title = bug_info
                bug_tr = ''.join(bug_info.target_release)
                bug_status = bug_info.status

                # We can have more then one commit per bug, no add twice into
                # wiki
                if bug_id in bz_data.values():
                    continue

                # Set target to correct git branch
                for branch in list(run_cmd(
                        _CMD_GET_BRANCHES).strip().split("\n")):

                    # Previously we had 3.3.0 branch, making compatible
                    if branch == "3.3.0" and bug_tr == "3.3.0":
                        break

                    if bug_tr == _DEFAULT_TARGET_RELEASE:
                        break

                    if branch != "3.3.0":
                        branch += "."
                        if branch in bug_tr:
                            bug_tr = branch[:-1]
                            break
                        else:
                            # Target release not related with current branch
                            continue

                bz_data['tr'] = bug_tr
                bz_data['title'] = str(bug_title)
                bz_data['id'] = bug_id
                bz_data['url'] = bug_url
                bz_data['status'] = bug_status
                bz_data['title'] = bz_data['title'].split(
                    "-", 1)[1].split("-", 1)[1]

                print "Processing commit related to:"
                print "==================================="
                print "Title: %s" % \
                    bz_data['title']
                print "Status: %s" % bz_data['status']
                print "Target Release: %s" % bz_data['tr']
                print "Bugzilla url: %s\n" % bz_data['url']
                list_bz_data.append(bz_data.copy())

    bug_rh_url.logout()


def write_data():
    """Create the result file"""

    _list_branches = list(run_cmd(_CMD_GET_BRANCHES).strip().split("\n"))
    _result_file = "result_branch_" + run_cmd(
        "git branch | grep \"*\" | cut -f 2 -d ' '").strip('\n') + ".txt"

    fd = open(_result_file, 'w', 0)

    fd.write("Branches wikified:\n")
    no_tg = []
    tg_with_no_branch = []
    bugs_diff_status = []

    for branch in _list_branches:
        fd.write("\n%s\n" % branch)
        fd.write("==========================================\n")
        cnt_bz_wiki = 0
        for bz in list_bz_data:
            if str(branch) == bz['tr']:
                if bz['status'] != "NEW" and bz['status'] != "ASSIGNED" and \
                        bz['status'] != "POST":
                    fd.write("{{BZ|%s}} - %s<BR>\n" % (bz['id'], bz['title']))
                    cnt_bz_wiki += 1
                    continue
                else:
                    bugs_diff_status.append(
                        "Title: %s\nTarget Release: %s\nStatus: %s"
                        "\nURL: %s\n\n" % (
                            bz['title'],
                            bz['tr'],
                            bz['status'],
                            bz['url']))
                continue
            elif _DEFAULT_TARGET_RELEASE == bz['tr']:
                no_tg.append("Title:%s\nURL: %s\nStatus: %s\n" % (
                    bz['title'],
                    bz['url'],
                    bz['status'])
                )
                continue

            if bz['tr'] not in _list_branches:
                tg_with_no_branch.append("Target Release: %s\nTitle: %s\nURL: "
                                         "%s\nStatus: %s\n" % (
                                         bz['tr'],
                                         bz['title'],
                                         bz['url'],
                                         bz['status']))

        fd.write("\nTotal: %d\n" % cnt_bz_wiki)

    # Show bugzillas in this branch with no ON_QA or MODIFIED
    if bugs_diff_status:
        fd.write("\nBUGZILLAS IN THIS BRANCH WITH NO ON_QA or MODIFIED \n")
        fd.write("=========================================================\n")

        for bz in set(bugs_diff_status):
            fd.write(bz)
        fd.write("Total: %d\n" % len(set(bugs_diff_status)))

    # If exists bugzillas with no target release, let's show
    if no_tg:
        fd.write("\nBUGZILLAS WITHOUT TARGET RELEASE\n")
        fd.write("==========================================\n")

        for bz in set(no_tg):
            fd.write(bz)
        fd.write("\nTotal: %d\n" % len(set(no_tg)))

    # Show bugzillas with target release but no branch available yet
    if tg_with_no_branch:
        fd.write("\nBUGZILLAS WITHOUT BRANCH YET OR UNKNOWN TARGET RELEASE\n")
        fd.write("========================================================\n")

        for bz in set(tg_with_no_branch):
            fd.write(bz)
        fd.write("\nTotal: %d\n" % len(set(tg_with_no_branch)))

    fd.close()

    print "See results in: %s" % _result_file

if __name__ == "__main__":
    """This script reads git log output and based on Bug-Url tag open the
    bugzilla and get target release and status data. If status is
    different of ASSIGNED, POST or NEW the script will provide the changelog
    for the current git branch in a wiki format.

    Additionally, the script shows:
      - Number of bugzillas without target release
      - Number of bugzillas with target release but without branch
      - Number of bugzillas with no modified or on_qa status
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Tool to analyze git log looking for Bug-Url tag',
        epilog='Example of use:\n%(prog)s '
                    '--bugzilla-user mysuperuser@mydomain.com '
                    '--bugzilla-pass my_super_bugzilla_pass '
                    '--clone-git-tree git://gerrit.ovirt.org/vdsm '
                    '--branch-to-analyze ovirt-3.4'
    )

    parser.add_argument(
        '--bugzilla-user',
        required=True,
        help="Bugzilla account"
    )

    parser.add_argument(
        '--bugzilla-pass',
        required=True,
        help="Bugzilla account password"
    )

    parser.add_argument(
        '--clone-git-tree',
        help="git tree to be cloned and analyzed"
    )

    parser.add_argument(
        '--branch-to-analyze',
        help="The branch which the tool will checkout"
    )
    args = parser.parse_args()

    if not args.bugzilla_user or not args.bugzilla_pass:
        raise RuntimeError(
            'You must provide your bugzilla account and password'
        )
    else:
        _BUGZILLA_USER = args.bugzilla_user
        _BUGZILLA_PASS = args.bugzilla_pass

    if not args.clone_git_tree and not os.path.isdir(".git"):
        raise RuntimeError(
            "You must execute inside a git tree! More info use --help"
        )

    if args.clone_git_tree and args.branch_to_analyze:
        cmd = "git clone " + args.clone_git_tree
        run_cmd(cmd)

        os.chdir(args.clone_git_tree.rpartition("/")[-1])

        cmd = "git checkout " + args.branch_to_analyze + " && " \
            "git log > " + _LOG_FILE_NAME
        run_cmd(cmd)

    else:
        if not os.path.isdir(".git"):
            raise RuntimeError(
                "You must execute inside a git tree! More info use --help"
            )

        cmd = "git log > " + _LOG_FILE_NAME
        run_cmd(cmd)

    collect_bugzilla_data()
    write_data()
