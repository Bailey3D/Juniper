"""
Library used for various python versioning uses
This module mainly just redirects functions defined in the juniper_bootstrap, as that module is a bit un-friendly for regular use
"""
import juniper.bootstrap


python_version = juniper.bootstrap.python_version
python_version_major = juniper.bootstrap.python_version_major
python_version_minor = juniper.bootstrap.python_version_minor
install_pip_packages = juniper.bootstrap.install_pip_packages
requirements_hash = juniper.bootstrap.requirements_hash
