"""
:type tool
:group Core
:category Core
:summary Launch a new explorer window at the root of the current Juniper
:icon icons\\standard\\folder.png
"""
import os

import juniper.paths


os.startfile(juniper.paths.root())
