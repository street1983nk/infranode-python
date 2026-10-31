[Deutsch](./README.md) | English

# infranode (Python)

Keyless Python client for the [InfraNode](https://infranode.dev) open-data API,
with ready-made [LangChain](https://www.langchain.com) and
[LlamaIndex](https://www.llamaindex.ai) tools.

InfraNode unifies open public data for **84 German cities** (weather, air quality,
electricity prices, land values, public transit, EV charging, demographics and
more) behind one JSON envelope. **No API key, no signup.**

```bash
pip install infranode
```

## Quickstart

```python
from infranode import InfraNode

api = InfraNode()
rec = api.weather("berlin")
print(rec.payload["temperature_c"], "degC")
print("Source:", rec.attribution["text"])   # always show attribution

# Any endpoint by name
fuel = api.record("hamburg", "fuel-prices")
muc = api.record("München", "weather")   # any spelling: München, muenchen, munich
cities = api.cities()                         # all 84 cities
```

Async works the same way:

```python
import asyncio
from infranode import AsyncInfraNode

async def main():
    async with AsyncInfraNode() as api:
        rec = await api.air("muenchen")
        print(rec.payload)

asyncio.run(main())
```

Every record carries its own `attribution` (source + license URL). The open-data
licenses require attribution, so display it to your users.

Errors come back as `InfraNodeError`:

```python
from infranode import InfraNode, InfraNodeError

try:
    InfraNode().record("essen", "wetter")  # wrong dataset name -> 404
except InfraNodeError as e:
    print(e.code, e.message, e.hint)  # hint: Meintest du 'weather'?
```

## Use it as an AI agent tool

### LangChain

```bash
pip install "infranode[langchain]"
```

```python
from infranode.integrations.langchain import infranode_tools

tools = infranode_tools()   # bind these to your LangChain agent / LLM
```

### LlamaIndex

```bash
pip install "infranode[llamaindex]"
```

```python
from infranode.integrations.llamaindex import infranode_tools

tools = infranode_tools()   # pass to your LlamaIndex agent
```

Both expose two tools: `infranode_get_city_data(city, dataset)` and
`infranode_list_cities()`. The tool description lists the valid datasets, so the
model can pick the right one. Prefer the official
[InfraNode MCP server](https://infranode.dev) (`https://mcp.infranode.dev/mcp`)
when your runtime speaks MCP; these tools are the lightweight alternative.

## Datasets

`weather`, `air`, `power-price`, `power-load`, `charging`, `sharing`,
`fuel-prices`, `pollen-uv`, `water-level`, `transit`, `station-departures`,
`demographics`, `land-values`, `election`, `tourism`, `accidents`, and more. The
full route list is at `https://infranode.dev/api/v1/openapi.yaml`.

## About InfraNode

- API: https://infranode.dev (keyless, rate limit 300 req/min/IP)
- MCP server: `https://mcp.infranode.dev/mcp`
- API source (Apache-2.0): https://github.com/street1983nk/infranode

## License

Apache-2.0. The data remains under the licenses of the respective sources,
surfaced via each record's `attribution` field.
