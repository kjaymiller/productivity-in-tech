from app import app
from flask import (
    render_template,
    redirect,
    url_for,
    session,
    request,
    Blueprint,
    )
from load_config import load_config

cfg = load_config('blueprints/vault/config.yml')

vault = Blueprint(
    'vault',
    __name__, 
    template_folder='templates',
    )

@vault.route('/')
def hello():
  return 'Hello World'
