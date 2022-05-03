"""
Library used for various python versioning uses
"""
import hashlib
import os
import pathlib
import subprocess
import sys

import juniper.paths
import juniper.utilities.json as json_utils


def python_version():
    """
    Return the python version (Major.Minor ONLY)
    :return <float:version> Formatted MAJOR.MINOR (Ie, 3.7)
    """
    return float(f"{sys.version_info[0]}.{sys.version_info[1]}")


def python_version_major():
    """
    :return <int:major> Returns the python major version (Ie, 3)
    """
    return int(str(python_version()).split(".")[0])


def python_version_minor():
    """
    :return <int:minor> Returns the python minor version (Ie, 10)
    """
    return int(str(python_version()).split(".")[1])


def install_pip_packages():
    """
    Installs the pip packages in the requirements.txt for the current Python interpereter / version
    """
    cached_requirements_hash = requirements_hash(cached=True)
    current_requirements_hash = requirements_hash(cached=False, update=False)
    site_packages_dir = pathlib.Path(juniper.paths.site_packages_dir()).resolve()
    if(
        not cached_requirements_hash or
        cached_requirements_hash != current_requirements_hash or
        not os.path.isdir(site_packages_dir) or
        not len(os.listdir(site_packages_dir))
    ):
        python_exe_path = pathlib.Path(juniper.paths.python_exe_path()).resolve()
        requirements_file_path = pathlib.Path(juniper.paths.get_config("python\\requirements.txt")).resolve()
        pip_wheel_path = pathlib.Path(os.path.join(juniper.paths.root(), "bin\\common\\python\\py3-none-any.whl")).resolve()
        cmd = f""""{python_exe_path}" "{pip_wheel_path}/pip" install -r "{requirements_file_path}" -t "{site_packages_dir}" """.replace("\\", "/")
        print(cmd)
        subprocess.call(cmd)
        requirements_hash(cached=False, update=True)


def requirements_hash(cached=False, update=True):
    """
    Gets a hash of the requirements.txt - either from the file or cached version
    :param [<bool:cached>] If true the cached version is retrieved
    :param [<bool:update>] Should the cache be updated?
    :return <str:hash> The file hash as a string - None if invalid
    """
    output = None
    python_key = f"python.{python_version_major()}{python_version_minor()}.requirements_hash"
    workspace_config = juniper.paths.get_config("client_settings.json.local")

    if(cached):
        output = json_utils.get_property(workspace_config, python_key)
    else:
        requirements_txt_path = juniper.paths.get_config("python\\requirements.txt")
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        with open(requirements_txt_path, 'rb') as f:
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(BLOCK_SIZE)
        output = str(file_hash.hexdigest())
        if(update):
            json_utils.set_file_property(workspace_config, python_key, output)
    return output
