# coding: utf-8

import os
import pytest

from pyrpkg import rpkgError
from mock import call
from munch import Munch

from base import Base

from dist_git.package_import import my_upload_fabric, import_package, setup_git_repo

import six

if six.PY3:
    from unittest import mock
    from unittest.mock import MagicMock
else:
    import mock
    from mock import MagicMock

from dist_git import providers


MODULE_REF = 'dist_git.package_import'


@pytest.yield_fixture
def mc_os_setgid():
    with mock.patch("{}.os.setgid".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_subprocess_check_output():
    with mock.patch("{}.subprocess.check_output".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_helpers():
    with mock.patch("{}.helpers".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_shutil():
    with mock.patch("{}.shutil".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_sync_branch():
    with mock.patch("{}.sync_branch".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_refresh_cgit_listing():
    with mock.patch("{}.refresh_cgit_listing".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_setup_git_repo():
    with mock.patch("{}.setup_git_repo".format(MODULE_REF)) as handle:
        yield handle


@pytest.yield_fixture
def mc_pyrpkg_commands():
    with mock.patch("{}.Commands".format(MODULE_REF)) as handle:
        yield handle


class TestPackageImport(Base):

    def test_my_upload(self, mc_os_setgid):
         filename = "source"
         source_path = os.path.join(self.tmp_dir_name, filename)
         with open(source_path, "w") as handle:
             handle.write("1")

         reponame = self.PROJECT_NAME
         target = "/".join([
             self.lookaside_location, reponame, filename, self.FILE_HASH, filename
         ])
         assert not os.path.exists(target)
         my_upload = my_upload_fabric(self.opts)
         my_upload("", reponame, source_path, self.FILE_HASH)
         assert os.path.isfile(target)

    def test_import_package(self, mc_pyrpkg_commands, mc_helpers, mc_shutil,
                            mc_sync_branch, mc_setup_git_repo, mc_refresh_cgit_listing):
        mc_cmd = MagicMock()
        mc_pyrpkg_commands.return_value = mc_cmd
        mc_cmd.commithash = '1234'

        mc_helpers.get_pkg_info = MagicMock()
        mc_helpers.get_pkg_info.return_value = Munch(name='pkgname', envr='1.2')

        namespace = 'somenamespace'
        branches = ['f25', 'f26']
        package_content = providers.PackageContent(spec_path='somepath')
        result = import_package(self.opts, namespace, branches, package_content)
        expected_result = Munch({
            'branch_commits': {'f26': '1234', 'f25': '1234'},
            'reponame': 'somenamespace/pkgname',
            'pkg_info': Munch({'envr': '1.2', 'name': 'pkgname'})
        })
        assert (result == expected_result)

        mc_cmd.push.side_effect = rpkgError
        result = import_package(self.opts, namespace, branches, package_content)
        expected_result = Munch({
            'branch_commits': {},
            'reponame': 'somenamespace/pkgname',
            'pkg_info': Munch({'envr': '1.2', 'name': 'pkgname'})
        })
        assert (result == expected_result)


    def test_setup_git_repo(self, mc_subprocess_check_output):
        reponame = 'foo'
        branches = ['f25', 'f26']
        setup_git_repo(reponame, branches)
        assert mc_subprocess_check_output.has_calls([
            call(['/usr/share/dist-git/setup_git_package', 'foo']),
            call(['/usr/share/dist-git/mkbranch', 'f25', 'foo']),
            call(['/usr/share/dist-git/mkbranch', 'f26', 'foo']),
        ])

    def refresh_cgit_listing(self, mc_subprocess_check_output):
        refresh_cgit_listing(self.opts)
        assert mc_subprocess_check_output.has_calls([
            call(["/usr/share/copr/dist_git/bin/cgit_pkg_list", self.opts.cgit_pkg_list_location])
        ])