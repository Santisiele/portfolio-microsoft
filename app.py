import logging

from flask import Flask
from flask_session import Session
from cachelib.file import FileSystemCache
from werkzeug.middleware.proxy_fix import ProxyFix

import config
from core import start_request, log_request
from routes import register_blueprints

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = config.FLASK_SECRET_KEY

app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_CACHELIB"] = FileSystemCache(cache_dir="flask_session", threshold=500)
Session(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app.before_request(start_request)
app.after_request(log_request)

register_blueprints(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000)