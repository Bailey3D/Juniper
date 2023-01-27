"""
:type tool
:group Core
:category Core
:summary Launch a new explorer window at the root of the current Juniper
:icon icons\\standard\\folder.png
"""
import os

import juniper.engine.paths


os.startfile(juniper.engine.paths.root())
