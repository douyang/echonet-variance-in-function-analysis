"""Sets paths based on configuration file."""

import os
import types
import configparser

_FILENAME = None
_PARAM = {}
for filename in ["data.cfg",
                 ".data.cfg",
                 os.path.expanduser("~/data.cfg"),
                 os.path.expanduser("~/.data.cfg"),
                 ]:
    if os.path.isfile(filename):
        _FILENAME = filename
        config = configparser.ConfigParser()
        with open(filename, "r") as f:
            config.read_string("[config]\n" + f.read())
            _PARAM = config["config"]
        break

CONFIG = types.SimpleNamespace(
    FILENAME=_FILENAME,
    DATA_DIR=_PARAM.get("data_dir", "EchoData/"))
