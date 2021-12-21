import toml
import os
import subprocess
"""Top-level package for epcsunspecdemo."""


#get version from toml
parent_dir = os.path.realpath(".")
toml_dict = toml.load(parent_dir + '/pyproject.toml')
__version__ = toml_dict['tool']['poetry']['version']