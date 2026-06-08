from flask import Blueprint

tele_bp = Blueprint('telemetria', __name__, url_prefix='/telemetria',
                    template_folder='../../templates/telemetria')

from . import routes  # noqa
