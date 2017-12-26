from app import app, mail
from flask import (
    render_template,
    redirect,
    url_for,
    session,
    request,
    Blueprint,
    )

vault = Blueprint(
    'vault',
    __name__, 
    template_folder='templates',
    )


@vault.route('/')
def vault_landing():
    return render_template('landing.html')
