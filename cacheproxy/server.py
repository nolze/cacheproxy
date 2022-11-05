from aiohttp import web, client_exceptions
from aiohttp_client_cache import CachedSession


class HandlerWithCache:
    def __init__(self, cache):
        self.cache = cache

    async def handle(self, request):
        url = request.match_info.get("url", None)
        # print(url)
        if not url:
            return web.HTTPBadRequest()
        query = request.query
        # print(query)
        if request.method == "GET" or request.method == "HEAD":
            async with CachedSession(cache=self.cache) as session:
                try:
                    remote_resp = await session.get(
                        "https://{}".format(url), params=query
                    )
                except client_exceptions.ClientConnectorError:
                    remote_resp = await session.get(
                        "http://{}".format(url), params=query
                    )
                # print(remote_resp.headers)
        # if request.method == "POST":
        #     form = await request.post()
        #     async with CachedSession(cache=self.cache) as session:
        #         remote_resp = await session.post("https://{}".format(url), params=query)

        # https://github.com/aio-libs/aiohttp/issues/3877
        resp = web.Response(headers=remote_resp.headers)
        # print(remote_resp.headers)
        for k in ["Content-Length", "Content-Encoding", "Transfer-Encoding"]:
            if k in resp.headers:
                del resp.headers[k]
        body = await remote_resp.read()
        resp.body = body
        # print(resp.headers)
        return resp
