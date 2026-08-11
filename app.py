from flask import Flask
from flask_session import Session
from cachelib.file import FileSystemCache
from werkzeug.middleware.proxy_fix import ProxyFix

import config
from routes import register_blueprints

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = config.FLASK_SECRET_KEY

app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_CACHELIB"] = FileSystemCache(cache_dir="flask_session", threshold=500)
Session(app)

register_blueprints(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000)