from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html.j2'), 404

@errors.app_errorhandler(500)
def page_not_found(error):
    return render_template('errors/500.html.j2'), 500
