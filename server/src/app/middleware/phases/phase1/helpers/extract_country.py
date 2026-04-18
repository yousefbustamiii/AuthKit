import asyncio
from functools import lru_cache

from starlette.requests import Request

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

class _GeoIPCache:
    def __init__(self):
        self._reader = None
        self.fn = None
        self._error_logged = False

    def lookup(self, reader, ip: str) -> str:
        if reader is not self._reader:
            self._reader = reader

            @lru_cache(maxsize=10_000)
            def fn(ip_addr: str) -> str:
                match = reader.get(ip_addr)
                if match and "country" in match and "iso_code" in match["country"]:
                    return match["country"]["iso_code"]
                return "Unknown"

            self.fn = fn
        return self.fn(ip)

_geoip_cache = _GeoIPCache()

async def extract_country(request: Request, ip: str) -> str:
    if not ip or ip in ("127.0.0.1", "::1", "localhost", "testclient"):
        return "Localhost"

    reader = request.app.state.geoip_reader
    loop = asyncio.get_running_loop()

    try:
        return await loop.run_in_executor(None, _geoip_cache.lookup, reader, ip)
    except Exception:
        if not _geoip_cache._error_logged:
            logger.exception("geoip_lookup_failed", extra={"ip_hash": hash_blake2s(ip, digest_size=5)})
            _geoip_cache._error_logged = True
        return "Unknown"
