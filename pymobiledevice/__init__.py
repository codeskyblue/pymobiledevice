# coding: utf-8
#

from __future__ import print_function

import os
import fnmatch
from pymobiledevice import lockdown
from pymobiledevice import apps
from pymobiledevice.afc import AFCShell
from pymobiledevice import afc


class PMDException(Exception):
    pass


class IDevice(object):
    def __init__(self, udid=None):
        self._udid = udid
        self._afcs = {}
        self._ldc = None

    def _new_lockdown(self):
        if self._ldc:
            return self._ldc
        self._ldc = lockdown.LockdownClient(udid=self._udid)
        return self._ldc

    def _new_afc(self, bundle_id):
        if bundle_id in self._afcs:
            return self._afcs[bundle_id]
        ldc = self._new_lockdown()
        self._afcs[bundle_id] = apps.house_arrest(ldc, bundle_id)
        return self._afcs[bundle_id]

    def close(self):
        """
        Stop all session
        """
        if self._afcs:
            for afc in self._afcs.values():
                afc.stop_session()
        self._afcs = {}

    def __del__(self):
        self.close()

    def app_listdir(self, bundle_id, path, absolute=False):
        """
        Args:
            absolute (bool): return full path
        """
        myafc = self._new_afc(bundle_id)
        ret = myafc.read_directory(path)
        paths = list(set(ret).difference(['.', '..']))
        if absolute:
            paths = [os.path.join(path, name) for name in paths]
        return paths

    def app_isdir(self, bundle_id, path):
        myafc = self._new_afc(bundle_id)
        finfo = myafc.get_file_info(path)
        if not finfo:
            return False
        return finfo['st_ifmt'] == 'S_IFDIR'

    def app_glob_files(self, bundle_id, globpath):
        """
        Return:
            list of matched paths
        """
        dirpath = os.path.dirname(globpath)
        paths = self.app_listdir(bundle_id, dirpath, absolute=True)
        return fnmatch.filter(paths, globpath)

    def app_pull(self, bundle_id, srcpath, dstpath, glob=False):
        """
        Pull file or directory from device to local
        """
        myafc = self._new_afc(bundle_id)

        if glob:
            paths = self.app_glob_files(bundle_id, srcpath)
            for p in paths:
                self.app_pull(bundle_id, p, dstpath)
            return

        finfo = myafc.get_file_info(srcpath)
        if not finfo:
            raise PMDException(srcpath, "not found")

        if finfo['st_ifmt'] == 'S_IFDIR':
            for filename in self.app_listdir(bundle_id, srcpath):
                if not os.path.isdir(dstpath):
                    os.makedirs(dstpath, 0o755)

                self.app_pull(bundle_id,
                              os.path.join(srcpath, filename),
                              os.path.join(dstpath, filename))
        else:
            data = myafc.get_file_contents(srcpath)
            with open(dstpath, 'wb') as f:
                f.write(data)  # TODO(ssx): should handle .plist file

        # self.app_listdir(srcpath)

    def app_rmdir(self, bundle_id, path):
        """
        Remove directory
        """
        c = self._new_afc(bundle_id)
        return c.remove_directory(path)

    def app_file_write_content(self, bundle_id, path, content):
        c = self._new_afc(bundle_id)
        return c.set_file_contents(path, content)

    def app_file_read_content(self, bundle_id, path):
        raise NotImplementedError()

    def app_remove(self, bundle_id, path, glob=False, recursive=False, check=False):
        """
        Remove file (support glob)

        Args:
            bundle_id (str): of app
            glob (bool): weather to support glob
            recursive (bool): when to recursive remove
            check (bool): enable it will raise PMDException when file not found

        Raises:
            PMDException
        """
        c = self._new_afc(bundle_id)
        if glob:
            remove_paths = self.app_glob_files(bundle_id, path)
            for p in remove_paths:
                self.app_remove(bundle_id, p, recursive=recursive, check=check)
            return
        if recursive:
            if self.app_isdir(bundle_id, path):
                paths = self.app_listdir(bundle_id, path, absolute=True)
                for p in paths:
                    self.app_remove(bundle_id, p, recursive=True, check=check)
                c.remove_directory(path)
                return
        ret = c.file_remove(path)
        if not check:
            return ret
        if ret == afc.AFC_E_OBJECT_NOT_FOUND:
            raise PMDException(path, "not found")
        elif ret == 0:
            return
        else:
            raise PMDException(path, "return code", ret)


if __name__ == '__main__':
    d = IDevice()
    bundle_id = "com.163.test"
    files = d.app_listdir(bundle_id, "/Documents/log", absolute=True)
    print("Files", '\n'.join(files))

    ret = d.app_remove(
        bundle_id, "/Documents/log/client0_log_old_*.txt", glob=True)
    print(ret)

    d.app_pull(bundle_id, "/Documents/", "iphonelog")
