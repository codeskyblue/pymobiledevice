#!/usr/bin/env python
# coding: utf-8
#

from __future__ import print_function

import os
import sys
import argparse
from pymobiledevice import lockdown
from pymobiledevice import apps
from pymobiledevice import afc
from pymobiledevice.afc import AFCShell


def _cmd_list(ldc, args):
    """
    Args:
        ldc: lockdown client
    """
    if not args.bundle_id:
        sys.exit("bundle_id is required")
    myafc = apps.house_arrest(ldc, args.bundle_id)
    target_dir = os.path.join("/Documents", args.path)
    d = myafc.read_directory(target_dir)
    if d:
        for f in d:
            print(os.path.join(args.path, f))
    myafc.stop_session()


def _cmd_rm(ldc, args):
    if not args.bundle_id:
        sys.exit("bundle_id is required")
    myafc = apps.house_arrest(ldc, args.bundle_id)
    print("Remove", args.path)
    ret = myafc.file_remove(os.path.join("/Documents", args.path))
    if ret == afc.AFC_E_OBJECT_NOT_FOUND:
        print("File not found")
    elif ret == 0:
        print("Delete success")
    else:
        print("Return code", ret)
    myafc.stop_session()


def main():
    parser = argparse.ArgumentParser(
        description="iOS Debug Bridge")
    parser.add_argument('-u', '--udid', dest='udid', help='device udid')
    parser.add_argument('-b', '--bundle_id',
                        dest='bundle_id', help='app bundle id')

    subparsers = parser.add_subparsers()

    plist = subparsers.add_parser("list", help='list app files')
    plist.add_argument("-p", "--path", default=".", help="target path")
    plist.set_defaults(func=_cmd_list)

    prm = subparsers.add_parser("rm")
    prm.add_argument("path", help="target path")
    prm.set_defaults(func=_cmd_rm)

    args = parser.parse_args()
    ldclient = lockdown.LockdownClient(udid=args.udid)
    args.func(ldclient, args)


if __name__ == '__main__':
    main()
