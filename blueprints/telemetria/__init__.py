from flask import Blueprint

tele_bp = Blueprint('telemetria', __name__, url_prefix='/telemetria')

from . import routes
