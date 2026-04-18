import asyncio
from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from pathlib import Path

import httpx
import orjson

from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent.parent / "data" / "cloudflare_ips.json"

type CfIpRanges = list[IPv4Network | IPv6Network]


def load_from_json() -> CfIpRanges:
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, "rb") as f:
                data = orjson.loads(f.read())
            v4: list[IPv4Network] = [ip_network(ip) for ip in data.get("ipv4", [])]
            v6: list[IPv6Network] = [ip_network(ip) for ip in data.get("ipv6", [])]
            return v4 + v6
    except Exception as e:
        logger.error("failed_to_load_cloudflare_ips", extra={"file": str(DATA_FILE), "error": str(e)})
    return []

async def refresh_cloudflare_ips(client: httpx.AsyncClient, current: CfIpRanges) -> CfIpRanges:
    try:
        v4_resp, v6_resp = await asyncio.gather(
            client.get("https://www.cloudflare.com/ips-v4"),
            client.get("https://www.cloudflare.com/ips-v6"),
        )

        v4_resp.raise_for_status()
        v6_resp.raise_for_status()

        new_v4_raw = [line.strip() for line in v4_resp.text.splitlines() if line.strip()]
        new_v6_raw = [line.strip() for line in v6_resp.text.splitlines() if line.strip()]

        current_data: dict = {}
        if DATA_FILE.exists():
            with open(DATA_FILE, "rb") as f:
                current_data = orjson.loads(f.read())

        if current_data.get("ipv4") == new_v4_raw and current_data.get("ipv6") == new_v6_raw:
            logger.info("cloudflare_ips_up_to_date")
            return current

        new_data = {"ipv4": new_v4_raw, "ipv6": new_v6_raw}
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_bytes(orjson.dumps(new_data, option=orjson.OPT_INDENT_2))
        tmp.replace(DATA_FILE)

        v4: list[IPv4Network] = [ip_network(ip) for ip in new_v4_raw]
        v6: list[IPv6Network] = [ip_network(ip) for ip in new_v6_raw]

        logger.info("successfully_updated_cloudflare_ips")
        return v4 + v6

    except Exception as e:
        logger.error("failed_to_refresh_cloudflare_ips", extra={"error": str(e)})
        return current


def is_cloudflare_ip(ip_str: str, ranges: CfIpRanges) -> bool:
    try:
        addr = ip_address(ip_str)
        return any(addr in network for network in ranges)
    except ValueError:
        return False