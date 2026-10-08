# Brave Search for Home Assistant

A Home Assistant custom integration that stores one Brave Search API key and makes web search available two ways: as a plain Home Assistant **service** that anything can call (automations, scripts, the REST/WebSocket API, or an external assistant's generic "call a Home Assistant service" tool), and as an **LLM tool** for Home Assistant's own Assist conversation agents.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![HACS](https://img.shields.io/badge/HACS-custom-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## Key features

- **`brave_search.search` service**: a plain Home Assistant service, callable from automations, scripts, the REST/WebSocket API, or any system that can already call Home Assistant services generically (no code on the caller's side needs to know anything about Brave or hold an API key - the key lives only in this integration). Returns the results directly as the service response.
- **`brave_search` LLM tool**: also registers a separate **Brave Search** LLM API (via `homeassistant.helpers.llm.async_register_api`), so a Home Assistant Assist conversation agent can search the internet even if its model has no native web access.
- Both share one implementation and one stored API key - the key is entered exactly once, in this integration's config flow.
- Config flow (UI only): paste your Brave Search API key, it is validated with a live test call before the entry is created.
- Single config entry: one Brave API key per Home Assistant instance.
- Returns a compact, friendly list of results (title, url, description) instead of raw API JSON.
- Graceful error handling for invalid keys, rate limits, and network failures.

## Prerequisites

- Home Assistant **2025.2.0** or newer (uses the `llm.API` / `async_register_api` mechanism in `homeassistant.helpers.llm`, see [Technical notes](#technical-notes)).
- A Brave Search API key, free tier available at [brave.com/search/api](https://brave.com/search/api/).
- [HACS](https://hacs.xyz/) installed, if installing this way.

## Installation (HACS)

1. In Home Assistant, go to **HACS → the three-dot menu (top right) → Custom repositories**.
2. Add this repository's URL and select category **Integration**.
3. Find **Brave Search** in HACS and install it.
4. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Brave Search**.
3. Paste your Brave Search API key and submit. The key is tested against the Brave API before the entry is saved.
4. That's it for the `brave_search.search` service - it is now callable by anything that can call a Home Assistant service (see below).
5. Optional, only if you want Home Assistant's own **Assist** voice pipeline to search the web directly: open **Settings → Voice assistants**, edit your Assist pipeline, open your conversation agent's own options (e.g. its "Control Home Assistant" / "LLM API" setting), and add **Brave Search** to the selected LLM API(s) — alongside **Assist**, if your conversation agent lets you pick more than one.

## Calling the service

`brave_search.search` works like any other Home Assistant service. It is read-only, so you must ask for the response.

- **Developer Tools → Actions** (or an automation/script action): action `brave_search.search`, data `{"query": "...", "count": 5}`, with "Response variable" / `response_variable` set so you can read the result.
- **REST API**, from anywhere that already holds a Home Assistant long-lived access token (e.g. another assistant's generic "call a Home Assistant service" tool):

  ```bash
  curl -X POST \
    -H "Authorization: Bearer <HA_TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"query": "mai időjárás Budapesten"}' \
    "http://<HA_HOST>:8123/api/services/brave_search/search?return_response=true"
  ```

  The caller never needs a Brave API key, only a Home Assistant token - the Brave key stays inside this integration.

## Configuration

| Name | Default | Description |
| --- | --- | --- |
| API key | (required) | Your Brave Search API key, entered once in the config flow. |

The service/tool itself accepts two parameters from the caller, there is nothing to configure for these:

| Parameter | Default | Range | Description |
| --- | --- | --- | --- |
| `query` | (required) | - | The search query text. |
| `count` | 5 | 1-10 | Number of results to return. |

## Project structure

```
ha-brave/
  hacs.json
  README.md
  custom_components/
    brave_search/
      __init__.py          # async_setup_entry / async_unload_entry, registers both
                            # the brave_search.search service and the LLM API
      manifest.json
      const.py
      config_flow.py        # API key form + live validation
      brave_llm.py           # async_search_brave (shared HTTP call) + BraveSearchTool
                              # + BraveSearchAPI (llm.API)
      services.yaml          # UI description/fields for brave_search.search
      strings.json
      translations/
        en.json
        hu.json
```

## Technical notes

This integration registers two things from one shared `async_search_brave` HTTP call in `brave_llm.py` (named that, not `llm.py`, specifically to avoid shadowing `homeassistant.helpers.llm` - a submodule of a package named the same as an absolute import used in that package's `__init__.py` silently overwrites it):

- A plain Home Assistant service, `brave_search.search`, via `hass.services.async_register(..., supports_response=SupportsResponse.ONLY)` - the standard mechanism for any read-only, data-returning Home Assistant service (the same kind `todo.get_items` or `calendar.get_events` use). This is what makes it callable by literally anything that can call a Home Assistant service, with the Brave API key never leaving this integration.
- Its own `llm.API` subclass (`BraveSearchAPI`) via `homeassistant.helpers.llm.async_register_api`, exposing a single `brave_search` `llm.Tool` - the same mechanism Home Assistant core itself uses for the built-in `assist` API (see `homeassistant/helpers/llm.py`). There is no supported hook for a third-party integration to silently inject a tool into another integration's existing LLM API, so this shows up as its own selectable LLM API; conversation agents that support selecting multiple LLM APIs can combine it with `assist`.

## Development and testing

There is no live Home Assistant instance bundled with this repository. To sanity-check the Python files:

```bash
python -m py_compile custom_components/brave_search/*.py
```

<details>
<summary>Troubleshooting</summary>

- **The service call returns nothing**: `brave_search.search` is read-only, you must request the response (`return_response=true` on the REST call, or set a "Response variable" in an automation/script action).
- **The LLM never calls the tool**: confirm the conversation agent has **Brave Search** selected among its LLM API(s), and that the Brave Search integration entry exists and is not in an error state.
- **"invalid_auth" during setup**: double-check the API key in the Brave Search dashboard; keys can be regenerated there.
- **"cannot_connect" during setup**: check the Home Assistant host's outbound internet access to `api.search.brave.com`.

</details>

---

## Brave Search Home Assistant integráció (magyar)

Ez az integráció egyetlen helyen tárolja a Brave Search API kulcsot, és kétféle módon ad webes keresést:

- **`brave_search.search` szolgáltatás**: egy sima Home Assistant szolgáltatás, amit bármi hívhat (automatizálás, script, REST/WebSocket API, vagy bármelyik másik rendszer, ami már tud generikusan Home Assistant szolgáltatást hívni - annak nem kell tudnia semmit a Brave-ről, nem kell neki API kulcs, a kulcs csak ebben az integrációban van).
- **`brave_search` LLM tool**: a Home Assistant saját Assist hangasszisztensének, hogy a beszélgetési ügynök (akár egy lokális LLM, amelynek nincs internet-hozzáférése) is tudjon keresni.

Mindkettő ugyanazt a kódot és ugyanazt az egyszer megadott API kulcsot használja.

### Telepítés HACS-on keresztül

1. A Home Assistantban: **HACS → jobb felső háromdot menü → Custom repositories**.
2. Add hozzá ennek a repónak az URL-jét, kategória: **Integration**.
3. Keresd meg a **Brave Search** integrációt a HACS-ban és telepítsd.
4. Indítsd újra a Home Assistantot.

### Beállítás

1. Menj a **Beállítások → Eszközök és szolgáltatások → Integráció hozzáadása** menübe.
2. Keresd meg a **Brave Search** integrációt.
3. Illeszd be a Brave Search API kulcsodat. A kulcs érvényességét egy teszthívással ellenőrizzük, mielőtt elmentjük.
4. A Brave Search API kulcsot a [brave.com/search/api](https://brave.com/search/api/) oldalon tudod beszerezni (van ingyenes csomag).
5. Ezzel a `brave_search.search` szolgáltatás már hívható bárhonnan, ami tud Home Assistant szolgáltatást hívni - pl. a Gunar `call_service` eszközével, `data={"query": "..."}` és `want_response=True` paraméterrel.
6. Opcionális, csak ha azt szeretnéd, hogy a Home Assistant saját **Assist** hangasszisztense is tudjon keresni: **Beállítások → Hangasszisztensek**, nyisd meg a beszélgetési ügynököd saját beállításait (pl. "LLM API" mező), és válaszd ki a **Brave Search** API-t is (az **Assist** mellett, ha engedi több API kiválasztását).

### Mit kell még neked elvégezned

- Saját Brave Search API kulcs beszerzése.
- A commitok push-olása a `szajbergyerek/ha-brave` GitHub repóba, hogy HACS custom repository-ként hozzáadható legyen.
