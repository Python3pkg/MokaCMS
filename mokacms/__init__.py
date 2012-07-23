from pyramid.config import Configurator
import logging
import sys
import pymongo
log = logging.getLogger(__name__)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    includeme(config)
    config.scan()
    return config.make_wsgi_app()

def add_routes(config, settings):

    config.add_static_view('static', 'static', cache_max_age=3600)

    api_prefix = settings.get("mokacms.api.prefix", "/api")
    if not api_prefix.startswith("/"):
        api_prefix = "/{}".format(api_prefix)
    try:
        api_version = int(settings.get("mokacms.api.version", "1"))
        if api_version < 0:
            raise ValueError("API version must be >0")

    except ValueError as e:
        log.critical(str(e))
        sys.exit(10)

    pfx = "{}/v{}".format(api_prefix, api_version)
    log.info("Setting up API with prefix {}".format(pfx))
    config.add_route("api", pfx)


def mongodb_connect(config, settings):
    conf = {s.replace("mongodb.", ""): settings[s]
            for s in settings
            if s.startswith("mongodb.") and "database" not in s}
    db = settings["mongodb.database"]

    log.info("Connection to mongodb: {}, database '{}'".format(conf, db))
    if "port" in conf:
        conf["port"] = int(conf["port"])

    # Override settings
    conf["auto_start_request"] = False

    config.registry.mongodb_settings = conf
    config.registry.mongodb_database = db
    try:
        config.registry.mongodb_connection = pymongo.Connection(**conf)

    except pymongo.errors.ConnectionFailure:
        log.exception("Cannot connect to MongoDB")
        sys.exit(11)

    config.set_request_property("mokacms.model.mongodb_start_request", 
                                name="mdb", reify=True)


def includeme(config):
    settings = config.get_settings()
    mongodb_connect(config, settings)
    add_routes(config, settings)
