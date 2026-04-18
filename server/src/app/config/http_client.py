import httpx

async def create_http_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=3.0,
            read=6.0,
            write=5.0,
            pool=2.0,
        ),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
        ),
        http2=True,
    )
    return client