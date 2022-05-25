import os

from flask import Flask, jsonify

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index_page():
        return jsonify({ 'hello': 'world' })

    from app.fcc import bp as fcc_bp
    app.register_blueprint(fcc_bp, url_prefix='/fcc')

    from app.sq import bp as sq_bp
    app.register_blueprint(sq_bp, url_prefix='/sq')

    from app.sq import db
    db.init_app(app)

    return app
