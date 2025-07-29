from infrastructure.configuration.cors_config import get_cors_middleware


def configure_middleware(app):
    app.add_middleware(get_cors_middleware)
