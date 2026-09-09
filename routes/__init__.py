from .main import bp as main_bp
from .auth import bp as auth_bp
from .portfolio import bp as portfolio_bp
from .accounting_entry import bp as accounting_bp
from .financial_panel import bp as panel_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(accounting_bp)
    app.register_blueprint(panel_bp)