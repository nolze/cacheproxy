import argparse
import logging
from pathlib import Path

from cacheproxy import server

logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())

parser = argparse.ArgumentParser()
parser.add_argument(
    "backend",
    nargs="?",
    choices=["memory", "file", "sqlite"],
    default="memory",
    help="Cache backend to use (default: %(default)s)",
)
parser.add_argument(
    "-p",
    "--port",
    type=int,
    dest="port",
    default=8080,
    help="Port to use (default: %(default)s)",
)
parser.add_argument(
    "-b",
    "--bind",
    dest="bind_address",
    default="0.0.0.0",
    help="Bind address to use (default: %(default)s)",
)
parser.add_argument(
    "-c",
    "--cache-name",
    type=Path,
    dest="cache_name",
    help="Cache filename",
)
parser.add_argument(
    "--temp",
    dest="use_temp",
    action="store_true",
    help="Store cache files in a temp directory",
)
parser.add_argument(
    "-e",
    "--expire-after",
    type=int,
    dest="expire_after",
    default=60 * 60,
    help="Time in seconds after which a cache entry will be expired "
    + "(-1: never expire, 0: expire immediately; default: %(default)s)",
)
parser.add_argument(
    "--allowed-codes",
    nargs="*",
    dest="allowed_codes",
    default=[200],
    help="Only cache responses with these status codes (default: %(default)s)",
)
parser.add_argument(
    "--allowed-methods",
    nargs="*",
    dest="allowed_methods",
    default=["GET", "POST", "HEAD"],
    help="Only cache requests with these HTTP methods (default: %(default)s)",
)
parser.add_argument(
    "--include-headers",
    dest="include_headers",
    action="store_true",
    help="Cache requests with different headers separately",
)
parser.add_argument(
    "--ignored_params",
    nargs="*",
    dest="ignored_params",
    help="Keep using the cached response even if these params change",
)
parser.add_argument(
    "--timeout",
    type=float,
    dest="timeout",
    help="database connection timeout (seconds)",
),
parser.add_argument(
    "-q",
    "--quiet",
    dest="quiet",
    action="store_true",
)
parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
)


def main():
    args = parser.parse_args()

    if args.quiet:
        pass
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s\n")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s\n")

    backend_options = {
        k: v
        for k, v in dict(
            cache_name=args.cache_name,
            use_temp=True if args.use_temp or not args.cache_name else False,
            expire_after=args.expire_after,
            # urls_expire_after={
            #     "*.fillmurray.com": -1
            # },
            allowed_codes=args.allowed_codes,
            allowed_methods=args.allowed_methods,
            include_headers=args.include_headers,
            ignored_params=args.ignored_params,
            timeout=args.timeout,
        ).items()
        if v is not None
    }

    if args.backend == "memory":
        # NOTE: https://aiohttp-client-cache.readthedocs.io/en/latest/modules/aiohttp_client_cache.backends.base.html#aiohttp_client_cache.backends.base.CacheBackend
        from aiohttp_client_cache import CacheBackend

        cache = CacheBackend(**backend_options)
    elif args.backend == "file":
        # NOTE: https://aiohttp-client-cache.readthedocs.io/en/latest/modules/aiohttp_client_cache.backends.filesystem.html#aiohttp_client_cache.backends.filesystem.FileBackend
        from aiohttp_client_cache import FileBackend

        cache = FileBackend(
            **{
                k: v
                for k, v in backend_options.items()
                if k in ["cache_name", "use_temp"]
            }
        )
        logger.info(f"Cache files: {cache.responses.cache_dir}")
    elif args.backend == "sqlite":
        # NOTE: https://aiohttp-client-cache.readthedocs.io/en/latest/modules/aiohttp_client_cache.backends.sqlite.html#aiohttp_client_cache.backends.sqlite.SQLiteBackend
        from aiohttp_client_cache import SQLiteBackend

        cache = SQLiteBackend(**backend_options)
        logger.info(f"Cache database: {cache.responses.filename}")
    else:
        raise Exception("Invalid backend name")

    app = server.web.Application()
    handler = server.HandlerWithCache(cache)
    app.add_routes([server.web.get("/{url:.+}", handler.handle)])

    server.web.run_app(app, host=args.bind_address, port=args.port)


if __name__ == "__main__":
    main()
