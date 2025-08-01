from infrastructure.configuration.cors_config import get_cors_middleware


def configure_middleware(app):
    get_cors_middleware(app)
