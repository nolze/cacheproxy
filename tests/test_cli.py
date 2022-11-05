import pytest
import unittest.mock as mock
from cacheproxy.cli import main
import logging


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8081)


@pytest.mark.asyncio
async def test_main(tmp_path, caplog, aiohttp_client, httpserver):
    # print(tmp_path / "cache")
    httpserver.expect_request("/ip").respond_with_json({"origin": "127.0.0.1"})

    with mock.patch(
        "sys.argv",
        ["main", "sqlite", "-c", str(tmp_path / "cache"), "-b", "localhost", "--debug"],
    ):
        with mock.patch("cacheproxy.server.web.run_app") as mocked_run_app:
            caplog.set_level(logging.DEBUG)
            main()
            (app,) = mocked_run_app.call_args.args
            server_kwargs = mocked_run_app.call_args.kwargs
            client = await aiohttp_client(app, server_kwargs=server_kwargs)

            # NOTE: 1st request
            resp = await client.get("/localhost:8081/ip")
            assert resp.status == 200
            data = await resp.json()
            assert data == {"origin": "127.0.0.1"}
            assert "Cached response found for key" not in caplog.text

            # NOTE: 2nd request
            resp = await client.get("/localhost:8081/ip")
            assert resp.status == 200
            data = await resp.json()
            assert data == {"origin": "127.0.0.1"}
            assert "Cached response found for key" in caplog.text
