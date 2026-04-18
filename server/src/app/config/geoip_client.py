import maxminddb

from server.src.app.config.settings import settings

def create_geoip_reader() -> maxminddb.Reader:
    return maxminddb.open_database(settings.geo_path)
