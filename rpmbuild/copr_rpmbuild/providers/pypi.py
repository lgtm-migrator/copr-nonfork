import logging
from ..helpers import run_cmd
from .base import Provider


log = logging.getLogger("__main__")


class PyPIProvider(Provider):
    def __init__(self, source_json, workdir=None, confdirs=None):
        super(PyPIProvider, self).__init__(source_json, workdir, confdirs)
        self.pypi_package_version = source_json["pypi_package_version"]
        self.pypi_package_name = source_json["pypi_package_name"]
        self.python_versions = source_json["python_versions"] or []

    def run(self):
        self.produce_srpm()

    def produce_srpm(self):
        cmd = ["pyp2rpm", self.pypi_package_name, "--srpm", "-d", self.workdir]

        for i, python_version in enumerate(self.python_versions):
            if i == 0:
                cmd += ["-b", str(python_version)]
            else:
                cmd += ["-p", str(python_version)]

        if self.pypi_package_version:
            cmd += ["-v", self.pypi_package_version]

        return run_cmd(cmd)