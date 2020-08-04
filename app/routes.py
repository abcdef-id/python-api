from app import app

class Route():
    def __init__(self):

        from app.apis.user import userapi
        app.register_blueprint(userapi, url_prefix='/api/v1/user')
