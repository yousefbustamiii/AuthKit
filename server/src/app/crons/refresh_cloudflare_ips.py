import asyncio

from fastapi import FastAPI
import httpx

from server.src.app.config.cloudflare_ip_ranges import load_from_json, refresh_cloudflare_ips
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

INTERVAL_SECONDS = 24 * 60 * 60  # exactly 24 hours


async def cloudflare_ip_refresh_cron(app: FastAPI, http: httpx.AsyncClient) -> None:
    while True:
        try:
            await asyncio.sleep(INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info("cloudflare_ip_refresh_cron_cancelled")
            break

        logger.info("cloudflare_ip_refresh_cron_triggered")

        current = app.state.cf_ip_ranges

        try:
            updated = await refresh_cloudflare_ips(http, current)
        except Exception:
            logger.exception("cloudflare_ip_refresh_cron_unexpected_error")
            updated = load_from_json() or current

        app.state.cf_ip_ranges = updated

        logger.info(
            "cloudflare_ip_refresh_cron_done",
            extra={"total_ranges": len(updated)},
        )
