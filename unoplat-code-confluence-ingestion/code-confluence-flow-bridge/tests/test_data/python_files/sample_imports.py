# Standard Library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

# Third Party
import pytest
import requests as req

# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
    ImportedName,
    UnoplatImport,
)
from src.code_confluence_flow_bridge.parser.python.utils.read_programming_file import (
    ProgrammingFileReader,
)

from ..common import constants

# Local imports
from .utils import helper
