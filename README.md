Deutsch | [English](https://github.com/street1983nk/infranode-python/blob/main/README.en.md)

# infranode (Python)

Python-Client ohne API-Key für die [InfraNode](https://infranode.dev) Open-Data-API,
mit fertigen Tools für [LangChain](https://www.langchain.com) und
[LlamaIndex](https://www.llamaindex.ai).

InfraNode bündelt offene Verwaltungsdaten aus **84 deutschen Städten** (Wetter,
Luftqualität, Strompreise, Bodenrichtwerte, ÖPNV, E-Ladepunkte, Demografie und
mehr) hinter einem einheitlichen JSON-Envelope. **Kein API-Key, keine Registrierung.**

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
muc = api.record("München", "weather")   # Schreibweise egal: München, muenchen, munich
cities = api.cities()                         # all 84 cities
```

Async funktioniert genauso:

```python
import asyncio
from infranode import AsyncInfraNode

async def main():
    async with AsyncInfraNode() as api:
        rec = await api.air("muenchen")
        print(rec.payload)

asyncio.run(main())
```

Jeder Record trägt seine eigene `attribution` (Quelle plus Lizenz-URL). Die
Open-Data-Lizenzen verlangen eine Quellenangabe, zeige sie also deinen Nutzern an.

Fehler kommen als `InfraNodeError` zurück:

```python
from infranode import InfraNode, InfraNodeError

try:
    rec = InfraNode().record("essen", "weather")
except InfraNodeError as e:
    print(e.code, e.message, e.hint)  # z. B. not_found oder upstream_unavailable
```

## Als Tool für KI-Agenten nutzen

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

Beide Integrationen liefern zwei Tools: `infranode_get_city_data(city, dataset)`
und `infranode_list_cities()`. Die Tool-Beschreibung listet die gültigen Datasets
auf, das Modell wählt also selbst das passende. Spricht deine Laufzeitumgebung
MCP, nimm besser den offiziellen
[InfraNode-MCP-Server](https://infranode.dev) (`https://mcp.infranode.dev/mcp`);
diese Tools sind die leichtgewichtige Alternative.

## Datasets

`weather`, `air`, `power-price`, `power-load`, `charging`, `sharing`,
`fuel-prices`, `pollen-uv`, `water-level`, `transit`, `station-departures`,
`demographics`, `land-values`, `election`, `tourism`, `accidents` und mehr. Die
vollständige Routenliste steht unter `https://infranode.dev/api/v1/openapi.yaml`.

## Über InfraNode

- API: https://infranode.dev (ohne API-Key, Rate-Limit 300 req/min/IP)
- MCP-Server: `https://mcp.infranode.dev/mcp`
- API-Quellcode (Apache-2.0): https://github.com/street1983nk/infranode

## Lizenz

Apache-2.0. Die Daten bleiben unter den Lizenzen der jeweiligen Quellen und sind
im `attribution`-Feld jedes Records ausgewiesen.
