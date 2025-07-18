# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""The main config file for Superset

All configuration in this file can be overridden by providing a superset_config
in your PYTHONPATH as there is a ``from superset_config import *``
at the end of this file.
"""

# Configuration loading is now handled by Flask's native methods in app.py
# This module serves as the default configuration loaded by Flask's from_object()
# The loading order and precedence is:
# 1. Flask loads this module (superset.config) via from_object()
# 2. Flask loads from SUPERSET_CONFIG_PATH via from_pyfile() if set
# 3. Flask loads superset_config module via from_object() if available
# 4. Flask loads environment variables with SUPERSET__ prefix via from_prefixed_env()

# Load all defaults from config_defaults.py (one-liner with Flask's from_object)
from superset.config_defaults import *  # noqa: F401,F403

# Explicitly import these attributes to ensure they are available for mypy
from superset.config_extensions import SupersetConfig  # noqa: F401
