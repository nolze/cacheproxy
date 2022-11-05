# CacheProxy

[![test](https://github.com/nolze/cacheproxy/actions/workflows/test.yaml/badge.svg)](https://github.com/nolze/cacheproxy/actions/workflows/test.yaml)
[![PyPI](https://img.shields.io/pypi/v/cacheproxy)](https://pypi.org/project/cacheproxy/)

A simple Python cache/caching proxy for Web development and something else, built on [aiohttp](https://github.com/aio-libs/aiohttp) and [aiohttp-client-cache](https://github.com/requests-cache/aiohttp-client-cache) (a family project of [requests-cache](https://github.com/requests-cache/requests-cache)).

Useful to avoid unfavorable massive accesses to external APIs during development, with little change, without preparing mocks. Not recommended for production.

## Install

```bash
pip install cacheproxy
```

## Usage

### 1. Start up proxy

```bash
$ cacheproxy sqlite -c ./cache --expire-after 1800
Cache database: /Users/nolze/src/cacheproxy/cache.sqlite

======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```

Other backends:

```bash
cacheproxy # in-memory
cacheproxy memory # in-memory
cacheproxy file -c ./cache # file-based, saved under ./cache/
cacheproxy sqlite -c ./cache # sqlite, saved to ./cache.sqlite
```

### 2. Access through proxy

cURL:

```bash
curl http://0.0.0.0:8080/api.github.com/repos/nolze/cacheproxy # This request is cached until the expiration time
# → {"id":...,"node_id":"...","name":"cacheproxy", ...
```

Python (requests):

```python
import requests

base_url = "http://0.0.0.0:8080/api.github.com" # Just replace with "https://api.github.com" on production
resp = requests.get(f"{base_url}/repos/nolze/cacheproxy") # or use urljoin()
print(resp.json())
# → {'id': ...., 'node_id': '....', 'name': 'cacheproxy', ...
```

JavaScript/Node:

```javascript
const baseURL = "http://0.0.0.0:8080/api.github.com"; // Just replace with "https://api.github.com" on production
const resp = await fetch(`${baseURL}/repos/nolze/cacheproxy`);
const data = await resp.json();
console.log(data);
// → Object { id: ..., node_id: "...", name: "cacheproxy", ...
```

### Interact with or modify cached data

Use [aiohttp-client-cache](https://github.com/requests-cache/aiohttp-client-cache) to load existing databases.

See also:

- <https://aiohttp-client-cache.readthedocs.io/>

## Todos

- [ ] Better error handling
- [ ] Write tests
- [ ] Better logging
- [ ] Support POST/PUT
- [ ] Support switching http/https (with --http/--https flags)
- [ ] Support DynamoDB, MongoDB, and Redis backends

## License

MIT
