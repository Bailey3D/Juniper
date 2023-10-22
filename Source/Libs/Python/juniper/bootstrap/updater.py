"""
:desc Validates all external PIP packages are installed
"""
import concurrent.futures
import functools
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
from subprocess import PIPE, run


class Updater(object):
    def __init__(self, juniper_engine):
        """
        Class used for updating Juniper / external dependencies
        """
        self.juniper_engine = juniper_engine

    def run(self, force=False):
        """
        Installs the pip packages in "Config\\Python\\requirements.txt" for the current host Python version (Major/Minor)
        Note: We must use `pathlib.Path("Some/Path").resolve()` as pip can fail to install on subst drives
        :param <bool:force> If True then the updater is force ran
        """
        cached_requirements_hash = self.cached_requirements_hash
        current_requirements_hash = self.current_requirements_hash
        site_packages_dir = self.juniper_engine.site_packages_dir
        if(
            not cached_requirements_hash or
            cached_requirements_hash != current_requirements_hash or
            not os.path.isdir(site_packages_dir) or
            not len(os.listdir(site_packages_dir)) or
            force
        ):
            python_path_resolved = pathlib.Path(self.juniper_engine.python_path).resolve()
            requirements_txt_path_resolved = pathlib.Path(self.python_requirements_file_path).resolve()
            pip_whl_path = pathlib.Path(self.pip_whl_path).resolve()

            # Setuptools can't be guarenteed to have been installed in all the host contexts
            # so install this first
            cmd = f""""{python_path_resolved}" "{pip_whl_path}/pip" install setuptools -t {site_packages_dir}""".replace("\\", "/")
            _ = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)

            # Package names
            package_names = []
            package_commands = []
            with open(requirements_txt_path_resolved, "r") as f:
                for line in f.readlines():
                    if(line.strip() and not line.startswith("#")):
                        package_names.append("TODO! Package names not provided - move to JSON")
                        package_commands.append(line.strip().split("==")[0])


            # TODO~ Juniper Engine: Updater - We need a way to prompt the user of an error on pip install
            # Threaded pip install
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(package_names)) as executor:
                futures = []
                for package_name, package_commands in zip(package_names, package_commands):
                    futures.append(executor.submit(self.install_pip_packages, package_name, [package_commands]))

                for future in concurrent.futures.as_completed(futures):
                    results = future.result()

            # Copy the Python3.dll to the shiboken2 directory in site packages
            # this will fix the issues with launching PySide2 within certain applications
            # (blender is the only known application that has this issue..)
            shiboken_site_packages_dir = os.path.join(site_packages_dir, "shiboken2")
            dll_path = os.path.join(
                os.path.dirname(self.juniper_engine.python_path),
                "python3.dll"
            )
            if(os.path.isfile(dll_path) and os.path.isdir(shiboken_site_packages_dir)):
                shutil.copyfile(dll_path, os.path.join(shiboken_site_packages_dir, "python3.dll"))

            self.update_requirements_hash()

    @property
    @functools.lru_cache()
    def python_requirements_file_path(self):
        """
        :return <str:path> The path to the `requirements.txt` file as stored in config
        """
        return os.path.join(self.juniper_engine.workspace_root, "Config\\Python\\requirements.txt")

    @property
    def python_requirements_cache(self):
        """
        :return <str:path> The path to the requirements hash json file
        """
        return os.path.join(self.juniper_engine.workspace_root, "Cached\\PyCache\\requirements_hashes.json")
    
    @property
    def pip_whl_path(self):
        """
        :return <str:path> The path to the pip wheel folder
        """
        return os.path.join(self.juniper_engine.workspace_root, "Binaries\\Python\\py3-none-any.whl").replace("\\", "/")

    @property
    def requirements_cache(self):
        """
        :return <dict:cache> The current cached data for the requirements.txt
        """
        if(os.path.isfile(self.python_requirements_cache)):
            with open(self.python_requirements_cache, "r") as f:
                return json.load(f)
        return {}

    def __get_file_hash(self, file_path):
        """
        Generates a hash for a file
        :param <str_file_path The file to get a hash for
        :return <str:hash> The hash of the input file
        """
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(BLOCK_SIZE)
        return str(file_hash.hexdigest())

    @property
    def current_requirements_hash(self):
        """
        :return <str:hash> The unique has for the current requirements.txt file
        """
        return self.__get_file_hash(self.python_requirements_file_path)

    @property
    def cached_requirements_hash(self):
        """
        :return <str:hash> The unique hash for the most recently installed requirements.txt file
        """
        python_key = f"Python{self.juniper_engine.python_version_major}.{self.juniper_engine.python_version_minor}"
        requirements_cache = self.requirements_cache
        if(python_key in requirements_cache):
            return requirements_cache[python_key]
        return None

    def update_requirements_hash(self):
        """
        Updates the `requirements_cache.json` file in the cached folder with the current
        cache of the requirements.txt file
        """
        json_data = self.requirements_cache

        python_key = f"Python{self.juniper_engine.python_version_major}.{self.juniper_engine.python_version_minor}"
        json_data[python_key] = self.current_requirements_hash

        with open(self.python_requirements_cache, "w") as f:
            json.dump(json_data, f)

    def install_pip_packages(self, package_name, package_commands):
        """
        This will install a pip package from an array of input commands

        Args:
            package_name (str): The name of the package to install
            package_commands (list): A list of commands to install the package
        """
        output = {
            "package_name": package_name,
            "package_commands": package_commands,
            "full_command": None,
            "success": True
        }
        pip_whl_path = self.pip_whl_path
        site_packages_dir = self.juniper_engine.site_packages_dir
        try:
            for command in package_commands:
                full_command = f"""{self.juniper_engine.python_path} "{pip_whl_path}/pip" install "{command}" -t "{site_packages_dir}" --no-cache-dir"""
                output["full_command"] = full_command
                run(full_command, stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            output["success"] = False

        return output
