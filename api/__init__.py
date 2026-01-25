from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from .server import *
from .auth import *
from .health import *
from .iam import *
