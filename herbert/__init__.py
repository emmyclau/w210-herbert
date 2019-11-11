import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from herbert.data.data_source import DataSource

db = SQLAlchemy()
ds = DataSource()


def create_app():
    app = Flask(__name__)

    # Bootstrap config
    Bootstrap(app)

    # Database config
    db_server = 'database-1.czlutn2hktjl.us-west-2.rds.amazonaws.com'
    db_port = 5432
    db_user = 'postgres'
    db_pw = os.environ['HERBERT_DB_PW']
    db_db = 'TestDB'

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pw}@{db_server}:{db_port}/{db_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

    db.init_app(app)

    # Import and register all blueprints
    from .views import errors
    app.register_blueprint(errors.bp)

    from .views import herb_views
    app.register_blueprint(herb_views.bp)

    from .views import home_views
    app.register_blueprint(home_views.bp)

    return app