from flask import Blueprint, render_template

bp = Blueprint('errors', __name__, template_folder='templates')


@bp.app_errorhandler(404)
def not_found(e):
    return render_template('404_jinja.html'), 404