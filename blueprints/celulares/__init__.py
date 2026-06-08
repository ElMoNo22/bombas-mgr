from flask import Blueprint

cel_bp = Blueprint('celulares', __name__, url_prefix='/celulares',
                   template_folder='../../templates/celulares')

from . import routes  # noqa
